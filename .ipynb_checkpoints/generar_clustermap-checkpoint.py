# generar_clustermap.py
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import os

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
# FUNCIÓN PRINCIPAL
# =====================================================

def plot_clustermap(matrix_df, annotations_df, selected_annotations, metodo="average",
                    figsize=(18, 20), xticklabels=False, yticklabels=False):

    row_colors_df = None
    if selected_annotations:
        row_colors_df = pd.DataFrame(index=matrix_df.index)
        for col in selected_annotations:
            row_colors_df[col] = annotations_df[col].map(color_palettes[col]).fillna("#FFFFFF")

    g = sns.clustermap(
        matrix_df,
        cmap="viridis",
        figsize=figsize,
        method=metodo,
        row_colors=row_colors_df,
        col_colors=row_colors_df,
        xticklabels=xticklabels,
        yticklabels=yticklabels
    )

    plt.setp(g.ax_heatmap.get_xticklabels(), fontsize=6, rotation=90)

    if not selected_annotations:
        return g

    # =====================================================
    # LEYENDAS EN DOS COLUMNAS
    # =====================================================
    legend_ax1 = g.fig.add_axes([1.03, 0.15, 0.15, 0.70])
    legend_ax2 = g.fig.add_axes([1.20, 0.15, 0.15, 0.70])

    legend_ax1.axis("off")
    legend_ax2.axis("off")

    mitad = (len(selected_annotations) + 1) // 2
    col1_annotations = selected_annotations[:mitad]
    col2_annotations = selected_annotations[mitad:]

    box_w = 0.028
    box_h = 0.028
    y_step_title = 0.06
    y_step_item = 0.028

    def draw_column(ax, annotations_list):
        y_cursor = 0.95
        for annotation in annotations_list:
            palette = color_palettes[annotation]

            ax.text(0.05, y_cursor, annotation, fontsize=11, fontweight="bold",
                    transform=ax.transAxes, va="top")

            y_cursor -= y_step_title

            for val, color in palette.items():
                ax.add_patch(plt.Rectangle((0.05, y_cursor - box_h/2),
                                           box_w, box_h,
                                           facecolor=color,
                                           edgecolor="black",
                                           transform=ax.transAxes))
                ax.text(0.05 + box_w + 0.02, y_cursor, str(val),
                        fontsize=9, va="center", transform=ax.transAxes)
                y_cursor -= y_step_item

            y_cursor -= 0.025

    draw_column(legend_ax1, col1_annotations)
    draw_column(legend_ax2, col2_annotations)

    return g
