# dendrograma_clusters.py
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster

# =====================================================
# Funciones auxiliares (mínimas necesarias)
# =====================================================

def clean_filename(filename):
    base = os.path.splitext(os.path.basename(filename))[0]
    if base.startswith("filtrado_"):
        base = base.replace("filtrado_", "", 1)
    for suf in ["_tumorales","_no_tumorales","_mieloides","_linfoides"]:
        if base.endswith(suf):
            base = base[:-len(suf)]
    return base

# (se dejan como compatibilidad, pero ya NO se usan)
def get_sample_type(filename):
    return "NA"

def get_fanconi_status(filename):
    return "NA"

def get_grado_displasia(filename):
    return "NA"

# =====================================================
# PALETAS NUEVAS
# =====================================================

type_colors = {
    'CIS': '#E41A1C',
    'HGD': '#FF7F00',
    'IC':  '#984EA3',
    'LGD': '#377EB8',
    'NT':  '#4DAF4A'
}

group_colors = {
    'FA': '#d73027',
    'Non FA': '#4575b4'
}

tumor_type_colors = {
    'Head and neck': '#FFB900',
    'Anogenital': '#5773CC'
}

gender_colors = {
    'female': '#8B2DB2',
    'male': '#3CB22D'
}

tumor_stage_colors = {
    'Stage 0': '#F0F921',
    'Stage I': '#FBA238',
    'Stage IB': '#F1605D',
    'Stage II': '#CC4678',
    'Stage III': '#9C179E',
    'Stage IIIA': '#6600A7',
    'Stage IIIB': '#3300A7',
    'Stage IVa': '#0D0887',
    'Stage IVc': '#06002A'
}

bmt_colors = {
    'Yes': '#009999',
    'No': '#CC5500'
}

desmo_colors = {
    'immature': '#EF9A9A',
    'intermediate': '#E53935',
    'mature': '#B71C1C',
    'none': '#CCCCCC'
}

# =====================================================
# Diccionario global
# =====================================================

color_palettes = {
    'Tipo': type_colors,
    'ROI': type_colors,
    'Group': group_colors,
    'Tumor.type': tumor_type_colors,
    'Tumor.stage': tumor_stage_colors,
    'Gender': gender_colors,
    'BMT': bmt_colors,
    'Desmoplastic.category': desmo_colors
}

# =====================================================
# FUNCIÓN PRINCIPAL
# =====================================================

def plot_dendrograma(matrix_df, annotations_df, selected_annotations=None,
                      metodo="average", K=4, figsize=(14,12),
                      xticklabels=False, yticklabels=False):

    samples = matrix_df.index.tolist()

    # =========================
    # COLORES DE ANOTACIONES
    # =========================
    col_colors_dict = {}

    for ann in selected_annotations:
        if ann not in annotations_df.columns:
            print(f"⚠ '{ann}' no está en annotations_df")
            continue

        palette = color_palettes.get(ann, {})

        values = annotations_df[ann].astype(str).str.strip()

        col_colors_dict[ann] = [
            palette.get(values.loc[s], "#FFFFFF") for s in samples
        ]

    col_colors = pd.DataFrame(col_colors_dict, index=samples)

    # =========================
    # LINKAGE Y CLUSTERS
    # =========================
    Z = linkage(matrix_df.values, method=metodo)
    clusters = fcluster(Z, K, criterion="maxclust")

    viridis = plt.get_cmap("viridis", K)
    cluster_colors = {i+1: mcolors.to_hex(viridis(i)) for i in range(K)}

    d_leaf = dendrogram(Z, no_plot=True)
    leaf_order = d_leaf["leaves"]
    leaf_cluster_map = {leaf_id: clusters[leaf_id] for leaf_id in leaf_order}

    node_cluster_map = {}
    n = len(matrix_df)

    for i, row in enumerate(Z):
        left = int(row[0])
        right = int(row[1])
        node_id = n + i

        left_c = leaf_cluster_map[left] if left < n else node_cluster_map.get(left)
        right_c = leaf_cluster_map[right] if right < n else node_cluster_map.get(right)

        node_cluster_map[node_id] = left_c if left_c == right_c else None

    def link_color_func(node_id):
        if node_id < n:
            c = leaf_cluster_map[node_id]
        else:
            c = node_cluster_map.get(node_id)

        return cluster_colors[c] if c is not None else "black"

    # =========================
    # CLUSTERMAP BASE (solo layout)
    # =========================
    g = sns.clustermap(
        matrix_df,
        method=metodo,
        metric="euclidean",
        col_colors=col_colors,
        cmap="gray",
        figsize=figsize
    )

    # Ocultar partes
    g.ax_heatmap.set_visible(False)
    g.ax_row_dendrogram.set_visible(False)

    if g.ax_row_colors is not None:
        g.ax_row_colors.set_visible(False)

    if g.cax is not None:
        g.cax.set_visible(False)

    # =========================
    # DENDROGRAMA SUPERIOR
    # =========================
    ax = g.ax_col_dendrogram
    ax.clear()

    dendrogram(
        Z,
        ax=ax,
        no_labels=True,
        link_color_func=link_color_func,
        color_threshold=0
    )

    # Línea de corte
    if K > 1:
        cut_height = Z[-K+1, 2]
        ax.axhline(cut_height, color="black", linestyle="dashed")

    ax.set_xticks([])
    ax.set_yticks([])

    g.fig.subplots_adjust(left=0.05, right=0.95, top=0.90, bottom=0.10)

    return g.fig


# =====================================================
# LEYENDAS
# =====================================================

def plot_legends(selected_annotations):

    n_annotations = len(selected_annotations)
    fig, axes = plt.subplots(1, n_annotations, figsize=(3*n_annotations, 2))

    if n_annotations == 1:
        axes = [axes]

    for ax, annotation in zip(axes, selected_annotations):

        ax.axis("off")

        if annotation not in color_palettes:
            continue

        palette = color_palettes[annotation]

        ax.set_title(annotation, fontsize=11, fontweight="bold")

        y_cursor = 0.9
        box_h = 0.6 / len(palette)

        for val, color in palette.items():

            ax.add_patch(
                plt.Rectangle((0, y_cursor - box_h/2), 0.2, box_h,
                              facecolor=color, edgecolor="black")
            )

            ax.text(0.22, y_cursor, str(val), va="center", fontsize=9)

            y_cursor -= box_h + 0.05

    fig.tight_layout()

    return fig