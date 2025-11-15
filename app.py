import streamlit as st
import pandas as pd
from generar_clustermap import (
    clean_filename, get_sample_type, get_fanconi_status,
    get_grado_displasia, generar_clustermap_interactivo
)

st.set_page_config(page_title="Clustermap Explorer", layout="wide")
st.title("🔬 Clustermap Explorer — FA vs No FA")

st.write("Sube tu matriz de distancias y tus metadatos para generar un clustermap interactivo.")

# =======================
# CARGA DE ARCHIVOS
# =======================
matriz_file = st.file_uploader("📂 Matriz de distancias (CSV)", type="csv")
meta_file = st.file_uploader("📂 Metadatos (CSV)", type="csv")

if matriz_file is None or meta_file is None:
    st.stop()

distancias = pd.read_csv(matriz_file, index_col=0)
metadata = pd.read_csv(meta_file)

metadata.columns = metadata.columns.str.strip()
metadata["Sample"] = metadata["Archivo"].apply(clean_filename)
metadata = metadata.set_index("Sample")

# Sincronizar nombres
distancias.index = [clean_filename(i) for i in distancias.index]
distancias.columns = distancias.index

# Añadir columnas derivadas
metadata["Tipo"] = [get_sample_type(m) for m in distancias.index]
metadata["Fanconi"] = [get_fanconi_status(m) for m in distancias.index]
metadata["Grado displasia"] = [get_grado_displasia(m) for m in distancias.index]

# =======================
# SIDEBAR: FILTROS
# =======================
st.sidebar.header("🎯 Filtros")

tipos = sorted(metadata["Tipo"].unique())
filtrar_tipos = st.sidebar.multiselect(
    "Tipos de muestra:",
    tipos,
    default=tipos
)

muestras = metadata[metadata["Tipo"].isin(filtrar_tipos)].index.tolist()

barras_disponibles = [
    "Tipo", "Fanconi", "Condition", "Gender",
    "Tumor stage", "BMT", "Desmoplastic category", "Grado displasia"
]

barras = st.sidebar.multiselect(
    "Barras de anotación:",
    barras_disponibles,
    default=["Tipo", "Fanconi"]
)

metodo = st.sidebar.selectbox(
    "Método de clustering",
    ["ward", "single", "complete", "average", "centroid", "median"],
    index=3
)

# =======================
# GENERAR MAPA
# =======================
st.subheader("📊 Clustermap:")

if len(muestras) < 3:
    st.warning("Selecciona al menos 3 muestras para generar un clustermap.")
    st.stop()

fig = generar_clustermap_interactivo(
    distancias,
    metadata,
    muestras,
    barras,
    metodo
)

st.pyplot(fig.fig)
