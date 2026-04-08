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
# Paletas de colores
# =====================================================

type_colors = {
    'carcinoma': '#1F990F',
    'dysplasia': '#1A66FF',
    'stroma-ad-carcinoma': '#8AE67E',
    'stroma-ad-dysplasia': '#80D4FF',
    'and-stroma': '#000000',
    'other': '#7f7f7f'
}

fanconi_colors = {'Fanconi': '#d73027', 'No Fanconi': '#4575b4'}
condition_colors = {'AG': '#FFB900', 'HN': '#5773CC'}
gender_colors = {'female': '#8B2DB2', 'male': '#3CB22D'}

tumor_stage_colors = {
    'Stage 0': '#F0F921', 'Stage I': '#FBA238', 'Stage IB': '#F1605D',
    'Stage II': '#CC4678', 'Stage III': '#9C179E', 'Stage IIIA': '#6600A7',
    'Stage IIIB': '#3300A7', 'Stage IVa': '#0D0887', 'Stage IVc': '#06002A'
}

bmt_colors = {'Yes': '#009999', 'No': '#CC5500'}

desmo_colors = {
    'immature': '#EF9A9A',
    'intermediate': '#E53935',
    'mature': '#B71C1C'
}

grado_colors = {
    'LG': '#D8AF97',
    'HG': '#996035',
    'Desconocido': '#FFFFFF'
}

tda_distance_colors = {
    'epithelium_100µm': '#FFEDA0',
    'epithelium_200µm': '#FED976',
    'epithelium_300µm': '#FEB24C',
    'epithelium_400µm': '#FD8D3C',

    'stroma_100µm': '#C7E9B4',
    'stroma_200µm': '#7FCDBB',
    'stroma_300µm': '#41B6C4',
    'stroma_400µm': '#1D91C0',
    'stroma_500µm': '#225EA8',
    'stroma_600µm': '#0C2C84',
    'stroma_700µm': '#08306B',
    'stroma_800µm': '#041F4A',
    'stroma_900µm': '#02101F'
}

color_palettes = {
    'Tipo': type_colors,
    'Fanconi': fanconi_colors,
    'Condition': condition_colors,
    'Gender': gender_colors,
    'Tumor stage': tumor_stage_colors,
    'BMT': bmt_colors,
    'Desmoplastic category': desmo_colors,
    'Grado displasia': grado_colors,
    'TDA_by_distance': tda_distance_colors
}

# =====================================================
# FUNCIÓN PRINCIPAL
# =====================================================

def plot_clustermap(matrix_df, annotations_df, selected_annotations,
                    metodo="average", figsize=(18, 20),
                    xticklabels=False, yticklabels=False):

    # Evita errores por columnas que NO existan
    annotations_df.columns = annotations_df.columns.str.strip()

    row_colors_df = None
    if selected_annotations:
        row_colors_df = pd.DataFrame(index=matrix_df.index)

        for col in selected_annotations:
            if col not in annotations_df.columns:
                print(f"⚠ Advertencia: La columna '{col}' no existe en annotations_df. Se omite.")
                continue

            # Mapea colores
            row_colors_df[col] = annotations_df[col].map(
                color_palettes.get(col, {})
            ).fillna("#FFFFFF")

    # Crear clustermap
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
            if annotation not in color_palettes:
                continue

            palette = color_palettes[annotation]

            ax.text(0.05, y_cursor, annotation, fontsize=11, fontweight="bold",
                    transform=ax.transAxes, va="top")
            y_cursor -= y_step_title

            for val, color in palette.items():
                ax.add_patch(plt.Rectangle((0.05, y_cursor - box_h / 2),
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