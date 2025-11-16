#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.gridspec import GridSpec
import seaborn as sns
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import squareform


# =========================================================
# FUNCIONES
# =========================================================

def generate_color_map(series):
    """Convierte una serie categórica en un mapa de colores fijo."""
    unique = series.unique()
    cmap = sns.color_palette("tab10", len(unique))
    color_dict = {val: cmap[i] for i, val in enumerate(unique)}
    return series.map(color_dict)


def plot_dendrogram_only(matrix_df, annotations_df, selected_annotations, method="average"):
    """
    Genera un dendrograma con barras de colores horizontales.
    """
    fig = plt.figure(figsize=(12, 6))
    gs = GridSpec(2, 1, height_ratios=[4, 0.6])

    # DENDROGRAMA
    ax_d = fig.add_subplot(gs[0])

    condensed = squareform(matrix_df.values, checks=False)
    Z = linkage(condensed, method=method)
    dendro = dendrogram(Z, labels=matrix_df.index, ax=ax_d)
    ax_d.set_xticks([])
    ax_d.set_ylabel("Distancia")

    reordered_labels = dendro["ivl"]

    # BARRAS DE COLOR
    ax_c = fig.add_subplot(gs[1])

    color_rows = []
    for col in selected_annotations:
        color_series = generate_color_map(annotations_df[col].loc[reordered_labels])
        # Convertir a RGB puros
        rgb = np.array(list(color_series.apply(lambda c: np.array(c)).values))
        color_rows.append(rgb)

    color_block = np.stack(color_rows)

    ax_c.imshow(color_block, aspect="auto")
    ax_c.set_yticks(range(len(selected_annotations)))
    ax_c.set_yticklabels(selected_annotations)
    ax_c.set_xticks([])

    return fig


def plot_clustermap(matrix_df, annotations_df, selected_annotations, method="average"):
    """
    Función del clustermap tradicional.
    """
    row_colors = None
    if selected_annotations:
        row_colors = {}
        for ann in selected_annotations:
            row_colors[ann] = generate_color_map(annotations_df[ann])
    
    cg = sns.clustermap(
        matrix_df,
        method=method,
        cmap="viridis",
        row_colors=row_colors,
        col_colors=row_colors,
        figsize=(10, 10)
    )
    return cg.fig


# =========================================================
# STREAMLIT UI
# =========================================================

st.title("🔬 Clustermap Explorer — TDA Data")

uploaded_matrix = st.file_uploader("📂 Subir matriz de distancia (CSV)", type=["csv"])
uploaded_annotations = st.file_uploader("📂 Subir anotaciones (CSV)", type=["csv"])

if uploaded_matrix and uploaded_annotations:
    matrix_df = pd.read_csv(uploaded_matrix, index_col=0)
    annotations_df = pd.read_csv(uploaded_annotations, index_col=0)

    st.success("Archivos cargados correctamente.")

    common = matrix_df.index.intersection(annotations_df.index)
    matrix_df = matrix_df.loc[common, common]
    annotations_df = annotations_df.loc[common]

    st.subheader("🎨 Seleccionar anotaciones para colorear")
    selected_annotations = st.multiselect(
        "Anotaciones disponibles:",
        list(annotations_df.columns),
        default=list(annotations_df.columns)
    )

    metodo = st.selectbox("Método de clustering", ["average", "single", "complete", "ward"])

    st.subheader("📌 Modo de visualización")
    modo = st.radio(
        "Selecciona cómo mostrar el árbol:",
        ["Clustermap completo", "Solo dendrograma + barras horizontales"]
    )

    if st.button("Generar"):
        if modo == "Clustermap completo":
            fig = plot_clustermap(matrix_df, annotations_df, selected_annotations, metodo)
            st.pyplot(fig)

        else:
            fig = plot_dendrogram_only(matrix_df, annotations_df, selected_annotations, metodo)
            st.pyplot(fig)
