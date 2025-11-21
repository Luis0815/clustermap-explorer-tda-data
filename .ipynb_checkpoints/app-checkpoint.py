# app.py
import streamlit as st
import pandas as pd
import os
import io
import importlib

st.set_page_config(layout="wide")
st.title("🔬 Explorador interactivo de Clustermaps TDA")

# ============================================================
# SELECCIÓN DEL MÓDULO DESDE LA INTERFAZ
# ============================================================

st.sidebar.header("⚙️ Configuración de módulo")
module_mode = st.sidebar.selectbox(
    "Selecciona el módulo a utilizar:",
    ["generar_clustermap.py", "dendrograma_clusters.py"]
)

# ============================================================
# IMPORTACIÓN SEGÚN LA OPCIÓN ELEGIDA
# ============================================================

if module_mode == "generar_clustermap.py":
    try:
        mod = importlib.import_module("generar_clustermap")
        plot_function = mod.plot_clustermap
        clean_filename = mod.clean_filename
        get_sample_type = mod.get_sample_type
        get_fanconi_status = mod.get_fanconi_status
        get_grado_displasia = mod.get_grado_displasia
        color_palettes = mod.color_palettes
        st.sidebar.success("Usando generar_clustermap.py")
    except Exception as e:
        st.error(f"❌ Error al cargar generar_clustermap.py: {e}")
        st.stop()

else:
    try:
        mod = importlib.import_module("dendrograma_clusters")
        plot_function = mod.plot_dendrograma
        clean_filename = mod.clean_filename
        get_sample_type = mod.get_sample_type
        get_fanconi_status = mod.get_fanconi_status
        get_grado_displasia = mod.get_grado_displasia
        color_palettes = mod.color_palettes
        st.sidebar.success("Usando dendrograma_clusters.py")
    except Exception as e:
        st.error(f"❌ Error al cargar dendrograma_clusters.py: {e}")
        st.stop()

# ============================================================
# Rutas base
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
PRELOADED_MATRIX_DIR = os.path.join(DATA_DIR, "matrices")
PRELOADED_METADATA_DIR = os.path.join(DATA_DIR, "anotaciones")

modo = st.radio("Selecciona la fuente de datos:", ["Usar archivos precargados", "Subir archivos manualmente"])

# ============================================================
# CARGA ARCHIVOS
# ============================================================

if modo == "Usar archivos precargados":

    matrices = [f for f in os.listdir(PRELOADED_MATRIX_DIR) if f.endswith(".csv")]
    selected_matrix = st.selectbox("📌 Selecciona matriz:", matrices)
    df = pd.read_csv(os.path.join(PRELOADED_MATRIX_DIR, selected_matrix), index_col=0)

    metadata_files = [f for f in os.listdir(PRELOADED_METADATA_DIR) if f.endswith(".csv")]
    selected_metadata = st.selectbox("📄 Selecciona metadatos:", metadata_files)
    metadata = pd.read_csv(os.path.join(PRELOADED_METADATA_DIR, selected_metadata))

else:
    metadata_file = st.file_uploader("📄 Metadatos (.csv)", type=["csv"])
    matrix_files = st.file_uploader("📁 Matrices de distancia (.csv)", type=["csv"], accept_multiple_files=True)

    if not (metadata_file and matrix_files):
        st.info("Sube metadatos y al menos una matriz.")
        st.stop()

    metadata = pd.read_csv(metadata_file)
    names = [m.name for m in matrix_files]
    selected_matrix_name = st.selectbox("📌 Matriz a visualizar:", names)
    matrix_file = next(m for m in matrix_files if m.name == selected_matrix_name)
    df = pd.read_csv(matrix_file, index_col=0)

# ============================================================
# ANOTACIONES
# ============================================================

cleaned = [clean_filename(i) for i in df.index]
df.index = cleaned
df.columns = cleaned

metadata["Sample"] = metadata["Archivo"].apply(clean_filename)
metadata = metadata.set_index("Sample")

annotations = pd.DataFrame(index=cleaned)
annotations["Tipo"] = [get_sample_type(n) for n in cleaned]
annotations["Fanconi"] = [get_fanconi_status(n) for n in cleaned]
annotations["Grado displasia"] = [get_grado_displasia(n) for n in cleaned]

for col in ["Condition", "Gender", "Tumor stage", "BMT", "Desmoplastic category"]:
    if col in metadata.columns:
        annotations[col] = metadata.reindex(cleaned)[col]

# ============================================================
# Clusters k (solo se aplica a dendrograma_clusters)
# ============================================================

K = st.slider("Número de clusters (K)", min_value=2, max_value=15, value=4)

# ============================================================
# CONTROLES
# ============================================================

st.subheader("🎛️ Anotaciones a mostrar")
selected_annotations = st.multiselect(
    "Selecciona anotaciones",
    list(color_palettes.keys()),
    default=["Tipo", "Fanconi"]
)

metodo = st.selectbox("Método de linkage", ["average", "ward", "single", "complete", "median"])

# ---- Subgrupos ----
st.subheader("🧪 Subgrupos")
subgrupos = {
    "Todos": cleaned,
    "Carcinoma": [s for s in cleaned if annotations.loc[s, "Tipo"] == "carcinoma"],
    "Dysplasia": [s for s in cleaned if annotations.loc[s, "Tipo"] == "dysplasia"],
    "Stroma-ad": [s for s in cleaned if "stroma" in annotations.loc[s, "Tipo"]],
    "Carcinoma + Dysplasia": [s for s in cleaned if annotations.loc[s, "Tipo"] in ["carcinoma", "dysplasia"]],
    "Fanconi": [s for s in cleaned if annotations.loc[s, "Fanconi"] == "Fanconi"],
    "No Fanconi": [s for s in cleaned if annotations.loc[s, "Fanconi"] == "No Fanconi"]
}

selected_group = st.selectbox("Subgrupo", list(subgrupos.keys()))
muestras = subgrupos[selected_group]

if len(muestras) < 3:
    st.warning("Subgrupo con menos de 3 muestras.")
    st.stop()

submatrix = df.loc[muestras, muestras]
subann = annotations.loc[muestras]

# ---- Tamaño figura ----
st.sidebar.header("📏 Tamaño de la figura")
fig_width = st.sidebar.slider("Ancho", 8, 30, 18)
fig_height = st.sidebar.slider("Alto", 8, 40, 20)

# ============================================================
# GENERAR FIGURA (usa el módulo elegido)
# ============================================================

if module_mode == "dendrograma_clusters.py":
    # plot_dendrograma acepta K
    fig_dendo = plot_function(
        submatrix,
        subann,
        selected_annotations=selected_annotations,
        metodo=metodo,
        K=K,
        figsize=(fig_width, fig_height),
        xticklabels=False,
        yticklabels=False
    )
    st.pyplot(fig_dendo)

    # -----------------------
    # Generar leyendas como figura separada
    # -----------------------
    if selected_annotations:
        fig_legends = mod.plot_legends(selected_annotations)
        st.pyplot(fig_legends)

else:
    # plot_clustermap NO acepta K
    fig_dendo = plot_function(
        submatrix,
        subann,
        selected_annotations=selected_annotations,
        metodo=metodo,
        figsize=(fig_width, fig_height),
        xticklabels=False,
        yticklabels=False
    )
    st.pyplot(fig_dendo)

# ===============================
# Exportar dendrograma
# ===============================
buf_png = io.BytesIO()
fig_dendo.savefig(buf_png, format="png", dpi=300, bbox_inches="tight")
buf_png.seek(0)
st.download_button("⬇️ Descargar PNG (Dendrograma)", buf_png, "dendrograma.png", "image/png")

buf_pdf = io.BytesIO()
fig_dendo.savefig(buf_pdf, format="pdf", bbox_inches="tight")
buf_pdf.seek(0)
st.download_button("⬇️ Descargar PDF (Dendrograma)", buf_pdf, "dendrograma.pdf", "application/pdf")

# ===============================
# Exportar leyendas (opcional)
# ===============================
if module_mode == "dendrograma_clusters.py" and selected_annotations:
    buf_legends = io.BytesIO()
    fig_legends.savefig(buf_legends, format="png", dpi=300, bbox_inches="tight")
    buf_legends.seek(0)
    st.download_button("⬇️ Descargar PNG (Leyendas)", buf_legends, "leyendas.png", "image/png")

