#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import os
import tempfile

# =====================================================
# Funciones auxiliares (copiadas de tu script)
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
# Función para graficar clustermap
# =====================================================

def plot_clustermap(matrix_df, annotations_df, selected_annotations, metodo="average"):
    row_colors_df = pd.DataFrame(index=matrix_df.index)

    for col in selected_annotations:
        colores = annotations_df[col].map(color_palettes[col]).fillna('#FFFFFF')
        row_colors_df[col] = colores

    g = sns.clustermap(
        matrix_df,
        cmap='viridis',
        figsize=(12, 14),
        row_colors=row_colors_df,
        col_colors=row_colors_df,
        method=metodo,
        xticklabels=True,
        yticklabels=False
    )

    plt.setp(g.ax_heatmap.get_xticklabels(), fontsize=6, rotation=90)

    return g


# =====================================================
# Streamlit APP
# =====================================================

st.title("🔬 Explorador interactivo de Clustermaps TDA")

st.write("Sube tu **carpeta con matrices de distancia** y tu **archivo de metadatos** para generar clustermaps con filtros y anotaciones.")


# ----------------------------
# CARGA DE ARCHIVOS
# ----------------------------

metadata_file = st.file_uploader("📄 Cargar archivo de metadatos (.csv)", type=["csv"])
matrix_files = st.file_uploader("📁 Cargar matrices de distancia (.csv)", type=["csv"], accept_multiple_files=True)

if metadata_file and matrix_files:
    metadata = pd.read_csv(metadata_file)
    metadata['Sample'] = metadata['Archivo'].apply(clean_filename)
    metadata = metadata.set_index("Sample")

    st.success("Archivos cargados correctamente.")

    # Seleccionar matriz
    nombres = [m.name for m in matrix_files]
    selected_matrix_name = st.selectbox("📌 Selecciona la matriz a visualizar", nombres)

    matrix_file = next(m for m in matrix_files if m.name == selected_matrix_name)
    df = pd.read_csv(matrix_file, index_col=0)

    # Limpieza de nombres
    cleaned = [clean_filename(i) for i in df.index]
    df.index = cleaned
    df.columns = cleaned

    # Crear anotaciones
    annotations = pd.DataFrame(index=cleaned)
    annotations['Tipo'] = [get_sample_type(n) for n in cleaned]
    annotations['Fanconi'] = [get_fanconi_status(n) for n in cleaned]
    annotations['Grado displasia'] = [get_grado_displasia(n) for n in cleaned]

    for col in ["Condition", "Gender", "Tumor stage", "BMT", "Desmoplastic category"]:
        if col in metadata:
            annotations[col] = metadata.reindex(cleaned)[col]

    # ----------------------------
    # FILTROS INTERACTIVOS
    # ----------------------------

    st.subheader("🎛️ Filtros de visualización")

    selected_annotations = st.multiselect(
        "Selecciona las anotaciones que quieres mostrar",
        list(color_palettes.keys()),
        default=["Tipo","Fanconi"]
    )

    metodo = st.selectbox("Método de linkage", ["average","ward","single","complete","median"])

    # Subgrupos
    st.subheader("🧪 Subgrupos de análisis")

    subgrupos = {
        "Todos": cleaned,
        "Carcinoma": [s for s in cleaned if annotations.loc[s,"Tipo"]=="carcinoma"],
        "Dysplasia": [s for s in cleaned if annotations.loc[s,"Tipo"]=="dysplasia"],
        "Stroma-ad": [s for s in cleaned if 'stroma' in annotations.loc[s,"Tipo"]],
        "Carcinoma + Dysplasia": [s for s in cleaned if annotations.loc[s,"Tipo"] in ["carcinoma","dysplasia"]],
        "Fanconi": [s for s in cleaned if annotations.loc[s,"Fanconi"]=="Fanconi"],
        "No Fanconi": [s for s in cleaned if annotations.loc[s,"Fanconi"]=="No Fanconi"]
    }

    selected_group = st.selectbox("Subgrupo a analizar", list(subgrupos.keys()))
    muestras = subgrupos[selected_group]

    if len(muestras) < 3:
        st.warning("Este subgrupo tiene menos de 3 muestras. No puede generarse un clustermap.")
    else:
        submatrix = df.loc[muestras, muestras]
        subann = annotations.loc[muestras]

        # ----------------------------
        # GENERAR HEATMAP
        # ----------------------------
        g = plot_clustermap(submatrix, subann, selected_annotations, metodo)

        st.pyplot(g.fig)

        st.success("Gráfico generado exitosamente.")