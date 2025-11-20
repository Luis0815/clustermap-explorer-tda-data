#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import io

# =====================================================
# CONFIGURACIÓN DE RUTAS (RELATIVAS)
# =====================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

PRELOADED_MATRIX_DIR = os.path.join(DATA_DIR, "matrices")
PRELOADED_METADATA_DIR = os.path.join(DATA_DIR, "anotaciones")

# =====================================================
# Funciones auxiliares
# =====================================================

def clean_filename(filename):
    base = os.path.splitext(os.path.basename(filename))[0]
    if base.startswith("filtrado_"):
        base = base.replace("filtrado_", "", 1)
    for suf in ["_tumorales","_no_tumorales","_mieloides","_linfoides"]:
        if base.endswith(suf):
            base = base[:-len(suf)]
    return base

def get_sample_type(filename):
    f = filename.lower()
    if '_and_stroma' in f or '-and-stroma' in f:
        return 'and-stroma'
    elif 'stroma_ad' in f and 'dysplasia' in f:
        return 'stroma-ad-dysplasia'
    elif 'stroma_ad' in f and 'carcinoma' in f:
        return 'stroma-ad-carcinoma'
    elif 'dysplasia' in f:
        return 'dysplasia'
    elif 'carcinoma' in f:
        return 'carcinoma'
    else:
        return 'other'

def get_fanconi_status(filename):
    return 'Fanconi' if 'F' in filename else 'No Fanconi'

def get_grado_displasia(filename):
    f = filename.lower()
    if 'lg' in f:
        return 'LG'
    elif 'hg' in f:
        return 'HG'
    else:
        return 'Desconocido'

# =====================================================
# Paletas de color
# =====================================================

type_colors = {
    'carcinoma': '#6B990F',
    'dysplasia': '#260F99',
    'stroma-ad-carcinoma': '#E5FFB2',
    'stroma-ad-dysplasia': '#BFB2FF',
    'and-stroma': '#000000',
    'other': '#7f7f7f'
}
fanconi_colors = {'Fanconi': '#d73027', 'No Fanconi': '#4575b4'}
condition_colors = {'AG': '#FFB900', 'HN': '#5773CC'}
gender_colors = {'female': '#E377C2', 'male': '#1F77B4'}
tumor_stage_colors = {
    'Stage 0': '#F0F921', 'Stage I': '#FBA238', 'Stage IB': '#F1605D',
    'Stage II': '#CC4678', 'Stage III': '#9C179E', 'Stage IIIA': '#6600A7',
    'Stage IIIB': '#3300A7', 'Stage IVa': '#0D0887', 'Stage IVc': '#06002A'
}
bmt_colors = {'Yes': '#2ca02c', 'No': '#d62728'}
desmo_colors = {'immature': '#EF9A9A', 'intermediate': '#E53935', 'mature': '#B71C1C'}
grado_colors = {'LG': '#81C784', 'HG': '#388E3C', 'Desconocido': '#FFFFFF'}

color_palettes = {
    'Tipo': type_colors,
    'Fanconi': fanconi_colors,
    'Condition': condition_colors,
    'Gender': gender_colors,
    'Tumor stage': tumor_stage_colors,
    'BMT': bmt_colors,
    'Desmoplastic category': desmo_colors,
    'Grado displasia': grado_colors
}

# =====================================================
# FUNCIÓN DE CLUSTERMAP (MODIFICADA)
# =====================================================

def plot_clustermap(matrix_df, annotations_df, selected_annotations, metodo="average"):
    row_colors_df = pd.DataFrame(index=matrix_df.index)

    for col in selected_annotations:
        colores = annotations_df[col].map(color_palettes[col]).fillna('#FFFFFF')
        row_colors_df[col] = colores

    g = sns.clustermap(
        matrix_df,
        cmap='viridis',
        figsize=(18, 20),        # ✔️ tamaño más grande
        row_colors=row_colors_df,
        col_colors=row_colors_df,
        method=metodo,
        xticklabels=False,
        yticklabels=False
    )

    plt.setp(g.ax_heatmap.get_xticklabels(), fontsize=5, rotation=90)  # ✔️ letra un poco más pequeña
    return g

# =====================================================
# STREAMLIT APP
# =====================================================

st.title("🔬 Explorador interactivo de Clustermaps TDA")

modo = st.radio(
    "Selecciona la fuente de datos:",
    ["Usar archivos precargados", "Subir archivos manualmente"]
)

# =====================================================
# MODO PRELOADED
# =====================================================

if modo == "Usar archivos precargados":

    if not os.path.exists(PRELOADED_MATRIX_DIR):
        st.error("❌ No existe la carpeta data/matrices/")
        st.stop()

    matrices = [f for f in os.listdir(PRELOADED_MATRIX_DIR) if f.endswith(".csv")]

    if len(matrices) == 0:
        st.error("❌ No hay matrices en data/matrices/")
        st.stop()

    selected_matrix = st.selectbox("📌 Selecciona matriz precargada", matrices)
    df = pd.read_csv(os.path.join(PRELOADED_MATRIX_DIR, selected_matrix), index_col=0)

    metadata_files = [f for f in os.listdir(PRELOADED_METADATA_DIR) if f.endswith(".csv")]

    if len(metadata_files) == 0:
        st.error("❌ No hay metadatos en data/anotaciones/")
        st.stop()

    selected_metadata = st.selectbox("📄 Selecciona archivo de metadatos", metadata_files)
    metadata = pd.read_csv(os.path.join(PRELOADED_METADATA_DIR, selected_metadata))

# =====================================================
# MODO MANUAL
# =====================================================

else:
    metadata_file = st.file_uploader("📄 Cargar metadatos", type=["csv"])
    matrix_file = st.file_uploader("📁 Cargar matriz de distancias", type=["csv"])

    if not (metadata_file and matrix_file):
        st.stop()

    metadata = pd.read_csv(metadata_file)
    df = pd.read_csv(matrix_file, index_col=0)

# =====================================================
# PROCESAR METADATOS
# =====================================================

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
    if col in metadata:
        annotations[col] = metadata.reindex(cleaned)[col]

# =====================================================
# FILTROS
# =====================================================

st.subheader("🎛️ Filtros de visualización")

selected_annotations = st.multiselect(
    "Selecciona anotaciones",
    list(color_palettes.keys()),
    default=["Tipo","Fanconi"]
)

metodo = st.selectbox("Método de linkage", ["average","ward","single","complete","median"])

# =====================================================
# GENERAR CLUSTERMAP
# =====================================================

g = plot_clustermap(df, annotations, selected_annotations, metodo)
st.pyplot(g.fig)

# =====================================================
# EXPORTAR FIGURA (NUEVO)
# =====================================================

st.subheader("💾 Exportar figura")

# PNG
buffer_png = io.BytesIO()
g.fig.savefig(buffer_png, format="png", dpi=300, bbox_inches="tight")
buffer_png.seek(0)

st.download_button(
    label="⬇️ Descargar PNG (alta resolución)",
    data=buffer_png,
    file_name="clustermap.png",
    mime="image/png"
)

# PDF
buffer_pdf = io.BytesIO()
g.fig.savefig(buffer_pdf, format="pdf", bbox_inches="tight")
buffer_pdf.seek(0)

st.download_button(
    label="⬇️ Descargar PDF (vectorial)",
    data=buffer_pdf,
    file_name="clustermap.pdf",
    mime="application/pdf"
)

st.success("Gráfico generado exitosamente.")
