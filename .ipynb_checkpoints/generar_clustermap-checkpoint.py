# generar_clustermap.py
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
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

def get_grado_displasia(filename):
    f = filename.lower()
    if 'lg' in f:
        return 'LG'
    elif 'hg' in f:
        return 'HG'
    else:
        return 'Desconocido'

# =====================================================
# Paletas de colores ACTUALIZADAS
# =====================================================

# ROI / Tipo
type_colors = {
    'CIS': '#E41A1C',
    'HGD': '#FF7F00',
    'IC':  '#984EA3',
    'LGD': '#377EB8',
    'NT':  '#4DAF4A',
    'other': '#7f7f7f'
}

# Group (Fanconi)
group_colors = {
    'FA': '#d73027',
    'Non FA': '#4575b4'
}

# Tumor type
tumor_type_colors = {
    'Head and neck': '#FFB900',
    'Anogenital': '#5773CC'
}

# Gender
gender_colors = {
    'female': '#8B2DB2',
    'male': '#3CB22D'
}

# Tumor stage
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

# BMT
bmt_colors = {
    'Yes': '#009999',
    'No': '#CC5500'
}

# Desmoplastic
desmo_colors = {
    'immature': '#EF9A9A',
    'intermediate': '#E53935',
    'mature': '#B71C1C',
    'none': '#CCCCCC'
}

# Grado displasia
grado_colors = {
    'LG': '#D8AF97',
    'HG': '#996035',
    'Desconocido': '#FFFFFF'
}

# Diccionario global
color_palettes = {
    'ROI': type_colors,
    'Tipo': type_colors,
    'Group': group_colors,
    'Tumor.type': tumor_type_colors,
    'Tumor.stage': tumor_stage_colors,
    'Gender': gender_colors,
    'BMT': bmt_colors,
    'Desmoplastic.category': desmo_colors,
    'Grado displasia': grado_colors
}

# =====================================================
# FUNCIÓN PRINCIPAL
# =====================================================

def plot_clustermap(matrix_df, annotations_df, selected_annotations,
                    metodo="average", figsize=(18, 20),
                    xticklabels=False, yticklabels=False):

    # ===============================
    # Limpieza básica
    # ===============================
    annotations_df.columns = annotations_df.columns.str.strip()

    # Asegurar que índices coincidan
    annotations_df = annotations_df.loc[matrix_df.index]

    # ===============================
    # Construir colores de filas
    # ===============================
    row_colors_df = None

    if selected_annotations:
        row_colors_df = pd.DataFrame(index=matrix_df.index)

        for col in selected_annotations:

            if col not in annotations_df.columns:
                print(f"⚠ Advertencia: '{col}' no existe en annotations_df")
                continue

            # Limpiar valores
            annotations_df[col] = annotations_df[col].astype(str).str.strip()

            palette = color_palettes.get(col, {})

            # Mapear colores
            row_colors_df[col] = annotations_df[col].map(palette)

            # Detectar valores no mapeados
            missing_vals = annotations_df[col][row_colors_df[col].isna()].unique()
            if len(missing_vals) > 0:
                print(f"⚠ Valores sin color en '{col}': {missing_vals}")

            row_colors_df[col] = row_colors_df[col].fillna("#FFFFFF")

    # ===============================
    # CLUSTERMAP
    # ===============================
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

    # ===============================
    # LEYENDAS (DOS COLUMNAS)
    # ===============================

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

            ax.text(0.05, y_cursor, annotation, fontsize=11,
                    fontweight="bold", transform=ax.transAxes, va="top")

            y_cursor -= y_step_title

            for val, color in palette.items():

                ax.add_patch(plt.Rectangle(
                    (0.05, y_cursor - box_h / 2),
                    box_w, box_h,
                    facecolor=color,
                    edgecolor="black",
                    transform=ax.transAxes
                ))

                ax.text(0.05 + box_w + 0.02, y_cursor, str(val),
                        fontsize=9, va="center", transform=ax.transAxes)

                y_cursor -= y_step_item

            y_cursor -= 0.025

    draw_column(legend_ax1, col1_annotations)
    draw_column(legend_ax2, col2_annotations)

    return g