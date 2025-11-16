# ============================================================
# 3. Alinear metadata con la matriz de distancia
# ============================================================

# Cargar metadata
metadata = pd.read_csv(metadata_file)

# --- LIMPIAR Y UNIFICAR NOMBRES ---
def clean_name(x):
    return (
        str(x)
        .replace(".csv", "")
        .replace(".txt", "")
        .replace("_dist", "")
        .replace("-dist", "")
        .strip()
    )

metadata["Archivo_limpio"] = metadata["Archivo"].apply(clean_name)
dist_index_clean = [clean_name(i) for i in distancias.index]

# --- FILTRAR METADATA SOLO PARA LAS MUESTRAS PRESENTES ---
metadata = metadata[metadata["Archivo_limpio"].isin(dist_index_clean)]

# --- REORDENAR metadata EN EL MISMO ORDEN QUE LA MATRIZ ---
metadata = metadata.set_index("Archivo_limpio").loc[dist_index_clean]

# Verificación (importante)
if len(metadata) != len(distancias):
    st.error(f"❌ Metadata ({len(metadata)}) y matriz ({len(distancias)}) no tienen el mismo número de muestras.")
    st.stop()

# ============================================================
# 4. Construir anotaciones de colores
# ============================================================

def simple_color_map(values):
    """Mapea valores únicos a colores hex sencillos."""
    unique = sorted(values.unique())
    palette = sns.color_palette("husl", len(unique))
    return {u: palette[i] for i, u in enumerate(unique)}

annot_cols = st.multiselect(
    "Selecciona columnas de metadata para colorear",
    metadata.columns,
    default=[c for c in metadata.columns if c not in ["Archivo", "Archivo_limpio"]]
)

# Crear diccionario de DataFrames de colores
row_colors = {}
for col in annot_cols:
    cmap = simple_color_map(metadata[col])
    row_colors[col] = metadata[col].map(cmap)

# ============================================================
# 5. Generar el clustermap
# ============================================================

st.write("### 🔍 Vista previa de la matriz de distancias")
st.dataframe(distancias)

fig = sns.clustermap(
    distancias,
    method=method,
    cmap="viridis",
    figsize=(10, 10),
    row_colors=[row_colors[c] for c in annot_cols],
    col_colors=[row_colors[c] for c in annot_cols]
)

st.pyplot(fig)
