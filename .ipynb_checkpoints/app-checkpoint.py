# app.py
import streamlit as st
import pandas as pd
import os
import io
import importlib

st.set_page_config(layout="wide")
st.title("🔬 Interactive TDA Clustermap Explorer")

# ============================================================
# MODULE SELECTION
# ============================================================

st.sidebar.header("Module Configuration")
module_mode = st.sidebar.selectbox(
    "Select the module to use:",
    ["generar_clustermap.py", "dendrograma_clusters.py"]
)

# ============================================================
# IMPORT MODULE
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
        st.sidebar.success("Using generar_clustermap.py")
    except Exception as e:
        st.error(f" Error loading generar_clustermap.py: {e}")
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
        st.sidebar.success("Using dendrograma_clusters.py")
    except Exception as e:
        st.error(f" Error loading dendrograma_clusters.py: {e}")
        st.stop()

# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
PRELOADED_MATRIX_DIR = os.path.join(DATA_DIR, "matrices")
PRELOADED_METADATA_DIR = os.path.join(DATA_DIR, "anotaciones")

modo = st.radio("Select data source:", ["Use preloaded files", "Upload files manually"])

# ============================================================
# LOAD FILES
# ============================================================

if modo == "Use preloaded files":

    matrices = [f for f in os.listdir(PRELOADED_MATRIX_DIR) if f.endswith(".csv")]
    selected_matrix = st.selectbox("📌 Select distance matrix:", matrices)
    df = pd.read_csv(os.path.join(PRELOADED_MATRIX_DIR, selected_matrix), index_col=0)

    metadata_files = [f for f in os.listdir(PRELOADED_METADATA_DIR) if f.endswith(".csv")]
    selected_metadata = st.selectbox("📄 Select metadata file:", metadata_files)
    metadata = pd.read_csv(os.path.join(PRELOADED_METADATA_DIR, selected_metadata))

else:
    metadata_file = st.file_uploader("📄 Metadata (.csv)", type=["csv"])
    matrix_files = st.file_uploader("📁 Distance matrices (.csv)", type=["csv"], accept_multiple_files=True)

    if not (metadata_file and matrix_files):
        st.info("Please upload metadata and at least one matrix.")
        st.stop()

    metadata = pd.read_csv(metadata_file)
    names = [m.name for m in matrix_files]
    selected_matrix_name = st.selectbox("📌 Select matrix to visualize:", names)
    matrix_file = next(m for m in matrix_files if m.name == selected_matrix_name)
    df = pd.read_csv(matrix_file, index_col=0)

# ============================================================
# ANNOTATIONS
# ============================================================

cleaned = [clean_filename(i) for i in df.index]
df.index = cleaned
df.columns = cleaned

metadata["Sample"] = metadata["Archivo"].apply(clean_filename)
metadata = metadata.set_index("Sample")

annotations = pd.DataFrame(index=cleaned)
annotations["Type"] = [get_sample_type(n) for n in cleaned]
annotations["Fanconi"] = [get_fanconi_status(n) for n in cleaned]
annotations["Dysplasia grade"] = [get_grado_displasia(n) for n in cleaned]

for col in ["Condition", "Gender", "Tumor stage", "BMT", "Desmoplastic category"]:
    if col in metadata.columns:
        annotations[col] = metadata.reindex(cleaned)[col]

# ============================================================
# K CLUSTERS (only for dendrograma_clusters)
# ============================================================

K = st.slider("Number of clusters (K)", min_value=2, max_value=15, value=4)

# ============================================================
# CONTROLS
# ============================================================

st.subheader("🎛️ Annotations to display")
selected_annotations = st.multiselect(
    "Select annotations",
    list(color_palettes.keys()),
    default=["Type", "Fanconi"]
)

metodo = st.selectbox("Linkage method", ["average", "ward", "single", "complete", "median"])

# ---- Subgroups ----
st.subheader("🧪 Subgroups")
subgrupos = {
    "All": cleaned,
    "Carcinoma": [s for s in cleaned if annotations.loc[s, "Type"] == "carcinoma"],
    "Dysplasia": [s for s in cleaned if annotations.loc[s, "Type"] == "dysplasia"],
    "Stroma-ad": [s for s in cleaned if "stroma" in annotations.loc[s, "Type"]],
    "Carcinoma + Dysplasia": [s for s in cleaned if annotations.loc[s, "Type"] in ["carcinoma", "dysplasia"]],
    "Fanconi": [s for s in cleaned if annotations.loc[s, "Fanconi"] == "Fanconi"],
    "Non-Fanconi": [s for s in cleaned if annotations.loc[s, "Fanconi"] == "No Fanconi"]
}

selected_group = st.selectbox("Subgroup", list(subgrupos.keys()))
muestras = subgrupos[selected_group]

if len(muestras) < 3:
    st.warning("Subgroup has fewer than 3 samples.")
    st.stop()

submatrix = df.loc[muestras, muestras]
subann = annotations.loc[muestras]

# ---- Figure size ----
st.sidebar.header("📏 Figure size")
fig_width = st.sidebar.slider("Width", 8, 30, 18)
fig_height = st.sidebar.slider("Height", 8, 40, 20)

# ============================================================
# GENERATE FIGURE
# ============================================================

if module_mode == "dendrograma_clusters.py":
    # plot_dendrograma accepts K
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

    # Legends as separate figure
    if selected_annotations:
        fig_legends = mod.plot_legends(selected_annotations)
        st.pyplot(fig_legends)

else:
    # plot_clustermap does NOT accept K
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
# EXPORT FIGURES
# ===============================

buf_png = io.BytesIO()
fig_dendo.savefig(buf_png, format="png", dpi=300, bbox_inches="tight")
buf_png.seek(0)
st.download_button("⬇️ Download PNG (Dendrogram)", buf_png, "dendrogram.png", "image/png")

buf_pdf = io.BytesIO()
fig_dendo.savefig(buf_pdf, format="pdf", bbox_inches="tight")
buf_pdf.seek(0)
st.download_button("⬇️ Download PDF (Dendrogram)", buf_pdf, "dendrogram.pdf", "application/pdf")

# ===============================
# EXPORT LEGENDS (optional)
# ===============================
if module_mode == "dendrograma_clusters.py" and selected_annotations:
    buf_legends = io.BytesIO()
    fig_legends.savefig(buf_legends, format="png", dpi=300, bbox_inches="tight")
    buf_legends.seek(0)
    st.download_button("⬇️ Download PNG (Legends)", buf_legends, "legends.png", "image/png")
