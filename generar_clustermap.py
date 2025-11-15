import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# === Funciones auxiliares ===

def clean_filename(filename):
    base = os.path.splitext(os.path.basename(filename))[0]

    if base.startswith("filtrado_"):
        base = base.replace("filtrado_", "", 1)

    sufijos = [
        "_tumorales",
        "_no_tumorales",
        "_mieloides",
        "_linfoides"
    ]
    for suf in sufijos:
        if base.endswith(suf):
            base = base[: -len(suf)]

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
    name = os.path.splitext(os.path.basename(filename))[0]
    return 'Fanconi' if 'F' in name else 'No Fanconi'

def get_grado_displasia(filename):
    f = filename.lower()
    if 'lg' in f:
        return 'LG'
    elif 'hg' in f:
        return 'HG'
    else:
        return 'Desconocido'


# === Paletas de color ===

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


# === Fun para la APP ===

def generar_clustermap_interactivo(distancias, metadata, muestras, barras, metodo):

    submatriz = distancias.loc[muestras, muestras]
    submeta = metadata.loc[muestras, barras]

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

    row_colors = pd.DataFrame(index=submeta.index)
    for col in barras:
        pal = color_palettes[col]
        row_colors[col] = submeta[col].map(pal)

    g = sns.clustermap(
        submatriz,
        cmap="viridis",
        figsize=(12, 15),
        row_colors=row_colors,
        col_colors=row_colors,
        method=metodo
    )

    return g
