# dendrograma_clusters.py
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster

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
    name = os.path.splitext(filename)[0]
    return 'Fanconi' if 'F' in name else 'No Fanconi'

def get_grado_displasia(filename):
    f = filename.lower()
    if 'lg' in f:
        return 'LG'
    elif 'hg' in f:
        return 'HG'
    else:
        return 'Desconocido'

# =====================================================
# Colores
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

desmo_colors = {
    'immature': '#EF9A9A',
    'intermediate': '#E53935',
    'mature': '#B71C1C'
}

grado_colors = {
    'LG': '#81C784',
    'HG': '#388E3C',
    'Desconocido': '#FFFFFF'
}

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
# Función principal
# =====================================================

def plot_dendrograma(matrix_df, annotations_df, selected_annotations=None,
                      metodo="average", K=4, figsize=(14,12), xticklabels=False, yticklabels=False):
    """
    Dendrograma superior con barras de color (col_colors) y clusters coloreados,
    sin mostrar heatmap, basado en el método de tu clustermap original.
    """
    # ------------------------
    # Preparar samples
    # ------------------------
    samples = matrix_df.index.tolist()
    
    # ------------------------
    # Colores de anotaciones
    # ------------------------
    col_colors_dict = {}
    for ann in selected_annotations:
        palette = color_palettes[ann]
        col_colors_dict[ann] = [palette.get(annotations_df.loc[s, ann], "#FFFFFF") for s in samples]
    col_colors = pd.DataFrame(col_colors_dict, index=samples)
    
    # ------------------------
    # Linkage y clusters
    # ------------------------
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

    # ------------------------
    # Crear clustermap para barras de color
    # ------------------------
    g = sns.clustermap(
        matrix_df,
        method=metodo,
        metric="euclidean",
        col_colors=col_colors,
        cmap="gray",
        figsize=figsize
    )

    # Ocultar heatmap y dendrograma izquierdo
    g.ax_heatmap.set_visible(False)
    g.ax_row_dendrogram.set_visible(False)
    if g.ax_row_colors is not None:
        g.ax_row_colors.set_visible(False)
    if g.cax is not None:
        g.cax.set_visible(False)
    
    # ------------------------
    # Dendrograma superior coloreado
    # ------------------------
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
    cut_height = Z[-K+1, 2]
    ax.axhline(cut_height, color="black", linestyle="dashed")
    
    ax.set_xticks([])
    ax.set_yticks([])
    g.fig.subplots_adjust(left=0.05, right=0.95, top=0.90, bottom=0.10)
    
    plt.show()
    return g.fig

# =====================================================
# Función para leyendas de anotaciones
# =====================================================
def plot_legends(selected_annotations):
    """
    Genera una figura separada con las leyendas de las anotaciones seleccionadas.
    """
    n_annotations = len(selected_annotations)
    fig, axes = plt.subplots(1, n_annotations, figsize=(3*n_annotations, 2))
    
    # Si solo hay una anotación, axes no es lista
    if n_annotations == 1:
        axes = [axes]
    
    for ax, annotation in zip(axes, selected_annotations):
        ax.axis("off")
        palette = color_palettes[annotation]
        
        # Título
        ax.set_title(annotation, fontsize=11, fontweight="bold")
        
        # Dibujar cada valor
        y_cursor = 0.9
        box_h = 0.6 / len(palette)  # Ajuste dinámico según cantidad de valores
        for val, color in palette.items():
            ax.add_patch(
                plt.Rectangle((0, y_cursor - box_h/2), 0.2, box_h, facecolor=color, edgecolor="black")
            )
            ax.text(0.22, y_cursor, str(val), va="center", fontsize=9)
            y_cursor -= box_h + 0.05
    
    fig.tight_layout()
    plt.show()
    return fig


