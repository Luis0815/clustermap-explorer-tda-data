<!-- # Clustermap Explorer

Aplicación web interactiva para generar clustermaps jerárquicos desde matrices de distancia con múltiples anotaciones (Tipo, Fanconi, Tumor Stage, BMT, Desmoplastic Category, Condition, etc.).

---

## Cómo usar

### 1. Selección del módulo
En la parte superior derecha de la interfaz encontrarás:

**⚙️ Configuración de módulo**  
Selecciona el módulo a utilizar:

- `generar_clustermap.py`: genera todo el clustermap con dendrograma y barras de color.  
- `dendrograma_clusters.py`: genera únicamente el dendrograma superior con barras de color, sin mostrar el heatmap completo.

---

### 2. Selecciona la fuente de datos

**Opciones:**

- **Usar archivos precargados**: selecciona una matriz y un archivo de metadatos ya disponibles en la carpeta `data`.  
- **Subir archivos manualmente**: sube tus propios archivos CSV.

#### Observaciones al subir archivos manualmente:

1. **Matriz de distancias**  
   - Debe ser cuadrada.  
   - La primera fila y columna debe contener los nombres de los archivos.  
   - Ejemplo:

    |   | HG_dysplasia_F23P1_PRIM_1.csv | HG_dysplasia_F23P1_PRIM_2.csv | HG_dysplasia_F29P1_1.csv |
    |---|-------------------------------|-------------------------------|---------------------------|
    | HG_dysplasia_F23P1_PRIM_1.csv | 0 | 8958.835963 | 8472.839855 |
    | HG_dysplasia_F23P1_PRIM_2.csv | 8958.835963 | 0 | 17237.43198 |
    | HG_dysplasia_F29P1_1.csv | 8472.839855 | 17237.43198 | 0 |

2. **Archivo de metadatos**  
   - Debe contener las siguientes columnas:

    | Archivo | Gender | Tumor stage | BMT | Desmoplastic category | Condition |
    |---------|--------|------------|-----|---------------------|----------|
    | stroma_ad_carcinoma_invasive_F23P1_PRIM_13.csv | female | Stage IVa | No | intermediate | HN |
    | carcinoma_invasive_F9P2_24.csv | female | Stage IIIB | No | intermediate | AG |
    | stroma_ad_carcinoma_invasive_HNSCC_7_7.csv | male | Stage III | No | mature | HN |

   - **Importante**: los nombres en la columna `Archivo` deben coincidir exactamente con los que aparecen en los nombres de la matriz de distancia.

---

### 3. Configuración de la visualización

Una vez cargados los archivos o seleccionados los precargados, podrás:

- Seleccionar las **anotaciones a mostrar** (por ejemplo: Tipo, Fanconi).  
- Elegir el **método de linkage** para clustering (`average`, `ward`, `single`, `complete`, `median`).  
- Filtrar los **subgrupos de interés** (Todos, Carcinoma, Dysplasia, Stroma-ad, Fanconi, No Fanconi, etc.).  
- Ajustar el **tamaño de la figura** desde la barra lateral.

Dependiendo del módulo seleccionado, se generará:

- **Clustermap completo** con dendrograma y barras de color.  
- **Solo dendrograma superior** con barras de color y opción de visualizar leyendas por anotación.

---

### 4. Exportar la figura

La aplicación permite descargar la figura en:

- **PNG**  
- **PDF**  

Si estás usando el módulo `dendrograma_clusters.py`, también puedes descargar la figura de las **leyendas de anotaciones** por separado.

---

### 5. Resumen rápido de pasos

1. Sube un archivo CSV con la matriz de distancias cuadrada.  
2. Sube un archivo CSV de metadatos.  
3. Selecciona:
   - Tipos de muestra y subgrupos de interés.  
   - Anotaciones a mostrar (barras de color).  
   - Método de clustering.  
4. La figura se generará automáticamente y podrás descargarla.

---

## Ejecutar localmente

```bash
git clone <repositorio>
cd clustermap-explorer-tda-data
pip install -r requirements.txt
streamlit run app.py
 -->

 # Clustermap Explorer

Interactive web application to generate hierarchical clustermaps from distance matrices with multiple annotations (Type, Fanconi, Tumor Stage, BMT, Desmoplastic Category, Condition, etc.).

---

## How to use

### 1. Module selection
In the top right corner of the interface you will find:

** Module Configuration**  
Select the module to use:

- `generar_clustermap.py`: generates the complete clustermap with dendrogram and color bars.  
- `dendrograma_clusters.py`: generates only the top dendrogram with color bars, without showing the complete heatmap.

---

### 2. Select data source

**Options:**

- **Use preloaded files**: select a matrix and metadata file already available in the `data` folder.  
- **Upload files manually**: upload your own CSV files.

#### Notes when uploading files manually:

1. **Distance matrix**  
   - Must be square.  
   - The first row and column must contain the file names.  
   - Example:

    |   | HG_dysplasia_F23P1_PRIM_1.csv | HG_dysplasia_F23P1_PRIM_2.csv | HG_dysplasia_F29P1_1.csv |
    |---|-------------------------------|-------------------------------|---------------------------|
    | HG_dysplasia_F23P1_PRIM_1.csv | 0 | 8958.835963 | 8472.839855 |
    | HG_dysplasia_F23P1_PRIM_2.csv | 8958.835963 | 0 | 17237.43198 |
    | HG_dysplasia_F29P1_1.csv | 8472.839855 | 17237.43198 | 0 |

2. **Metadata file**  
   - Must contain the following columns:

    | File | Gender | Tumor stage | BMT | Desmoplastic category | Condition |
    |---------|--------|------------|-----|---------------------|----------|
    | stroma_ad_carcinoma_invasive_F23P1_PRIM_13.csv | female | Stage IVa | No | intermediate | HN |
    | carcinoma_invasive_F9P2_24.csv | female | Stage IIIB | No | intermediate | AG |
    | stroma_ad_carcinoma_invasive_HNSCC_7_7.csv | male | Stage III | No | mature | HN |

   - **Important**: the names in the `File` column must exactly match those that appear in the distance matrix names.

---

### 3. Visualization configuration

Once files are loaded or preloaded ones are selected, you will be able to:

- Select the **annotations to display** (for example: Type, Fanconi).  
- Choose the **linkage method** for clustering (`average`, `ward`, `single`, `complete`, `median`).  
- Filter **subgroups of interest** (All, Carcinoma, Dysplasia, Stroma-ad, Fanconi, No Fanconi, etc.).  
- Adjust the **figure size** from the sidebar.

Depending on the selected module, it will generate:

- **Complete clustermap** with dendrogram and color bars.  
- **Only top dendrogram** with color bars and option to display legends per annotation.

---

### 4. Export the figure

The application allows you to download the figure in:

- **PNG**  
- **PDF**  

If you are using the `dendrograma_clusters.py` module, you can also download the **annotation legends** figure separately.

---

### 5. Quick step summary

1. Upload a CSV file with the square distance matrix.  
2. Upload a CSV metadata file.  
3. Select:
   - Sample types and subgroups of interest.  
   - Annotations to display (color bars).  
   - Clustering method.  
4. The figure will be generated automatically and you can download it.

---

## Run locally

```bash
git clone <repository>
cd clustermap-explorer-tda-data
pip install -r requirements.txt
streamlit run app.py