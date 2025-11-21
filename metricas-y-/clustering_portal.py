# ==============================================================
# 🤖 clustering_portal.py — Agrupamiento de noticias (K-Means)
# Autor: Jhon Alexnader Chambi Vilca
# Curso: Minería de Datos - Portal de Noticias Inteligente
# ==============================================================

import sys
import os
import logging
import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import LabelEncoder

import matplotlib.pyplot as plt
import seaborn as sns
import warnings

warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# --------------------------------------------------------------
# 📁 1. Cargar datos desde CSV
# --------------------------------------------------------------
archivo_csv = "noticias02.csv"   # <-- Cambia aquí si tu archivo tiene otro nombre

def try_read_csv(path):
    """Intenta leer el CSV en utf-8 y luego en latin1."""
    try:
        return pd.read_csv(path, encoding="utf-8", quotechar='"', on_bad_lines="skip")
    except Exception:
        try:
            return pd.read_csv(path, encoding="latin1", quotechar='"', on_bad_lines="skip")
        except Exception as e:
            logging.error(f"No se pudo leer el CSV: {e}")
            sys.exit(1)

if not os.path.exists(archivo_csv):
    logging.error(f"No se encontró el archivo '{archivo_csv}' en la carpeta actual.")
    sys.exit(1)

df = try_read_csv(archivo_csv)

# --------------------------------------------------------------
# 🔡 2. Normalizar nombres de columnas y detectar campos clave
# --------------------------------------------------------------
def normalize(name: str) -> str:
    s = str(name).strip().lower()
    replace_map = {"á":"a", "é":"e", "í":"i", "ó":"o", "ú":"u", "ñ":"n"}
    for k, v in replace_map.items():
        s = s.replace(k, v)
    s = s.replace(" ", "_").replace("-", "_")
    return s

orig_columns = list(df.columns)
cols_norm = [normalize(c) for c in orig_columns]

def find_col(orig_cols, norm_cols, candidates):
    for cand in candidates:
        for orig, norm in zip(orig_cols, norm_cols):
            if norm == cand or cand in norm:
                return orig
    return None

# título
title_candidates = ["titulo", "titular", "title", "headline"]
title_col = find_col(orig_columns, cols_norm, title_candidates)

# descripción (opcional)
desc_candidates = ["descripcion", "resumen", "texto", "contenido"]
desc_col = find_col(orig_columns, cols_norm, desc_candidates)

# categoría (solo para análisis posterior, no es obligatoria para clustering)
cat_candidates = ["categoria", "category", "etiqueta", "label"]
cat_col = find_col(orig_columns, cols_norm, cat_candidates)

if title_col is None:
    logging.error("No se encontró una columna de título en el CSV.")
    logging.info(f"Columnas detectadas: {orig_columns}")
    sys.exit(1)

# Renombrar lo que encontremos
rename_map = {title_col: "titulo"}
if desc_col:
    rename_map[desc_col] = "descripcion"
if cat_col:
    rename_map[cat_col] = "categoria"

df = df.rename(columns=rename_map)

# Limpiar campos de texto
df["titulo"] = df["titulo"].astype(str).str.strip()
if "descripcion" in df.columns:
    df["descripcion"] = df["descripcion"].astype(str).str.strip()
if "categoria" in df.columns:
    df["categoria"] = df["categoria"].astype(str).str.strip()

# Eliminar filas sin título
df = df.replace({"titulo": {"nan": np.nan}})
df = df.dropna(subset=["titulo"])

logging.info(f"✅ Datos cargados. Filas: {len(df)}, columnas: {list(df.columns)}")

# --------------------------------------------------------------
# 🧹 3. Preparar texto para clustering
# --------------------------------------------------------------
if "descripcion" in df.columns:
    textos = (df["titulo"] + " " + df["descripcion"]).str.strip()
else:
    textos = df["titulo"]

# Stopwords en español (mismo enfoque que metricas_portal.py)
def get_spanish_stopwords():
    try:
        import nltk
        from nltk.corpus import stopwords
        try:
            sw = set(stopwords.words("spanish"))
        except Exception:
            nltk.download("stopwords", quiet=True)
            sw = set(stopwords.words("spanish"))
        return list(sw)
    except Exception:
        return [
            "a","al","algo","algunas","algunos","ante","antes","como","con","contra","cual","cuando",
            "de","del","desde","donde","dos","el","ella","ellas","ellos","en","entre","era","erais",
            "eran","eras","es","esta","estaba","estabais","estaban","estabas","estad","estada",
            "estadas","estados","estados","estais","estamos","estan","estando","estar","estas",
            "este","esto","estos","estoy","fue","fueron","fui","fuimos","ha","hace","haces","hacia",
            "hasta","hay","incluso","la","las","lo","los","me","mi","mis","mucho","muy","ni","no",
            "nos","nosotros","o","os","otra","otros","para","pero","por","porque","que","quien",
            "quienes","se","sea","ser","si","sido","sin","sobre","su","sus","tambien","tan","tener",
            "tiene","tienen","toda","todas","todo","todos","tu","tus","un","una","uno","unos","usted",
            "vosotros","y","ya"
        ]

spanish_stopwords = get_spanish_stopwords()

# Vectorización TF-IDF
vectorizer = TfidfVectorizer(
    stop_words=spanish_stopwords,
    max_features=2000
)
X = vectorizer.fit_transform(textos)
logging.info(f"🔡 Vectorización completada. Dimensiones TF-IDF: {X.shape}")

# --------------------------------------------------------------
# 🔍 4. Búsqueda de k óptimo con silueta
# --------------------------------------------------------------
k_values = [4, 5, 6, 7, 8, 9, 10]
sil_scores = []

for k in k_values:
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(X)
    score = silhouette_score(X, labels)
    sil_scores.append(score)
    logging.info(f"k = {k} → silueta = {score:.3f}")

best_idx = int(np.argmax(sil_scores))
best_k = k_values[best_idx]
best_sil = sil_scores[best_idx]

logging.info(f"🏆 Mejor k según silueta: k = {best_k} (score = {best_sil:.3f})")

# Guardar tabla de silueta
df_sil = pd.DataFrame({"k": k_values, "silhouette": sil_scores})
df_sil.to_csv("silhouette_scores.csv", index=False)

# Plot Silueta vs k
plt.figure(figsize=(6,4))
plt.plot(k_values, sil_scores, marker="o")
plt.xlabel("Número de clusters (k)")
plt.ylabel("Silueta promedio")
plt.title("Silueta promedio vs número de clusters")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("silhouette_vs_k.png", dpi=300)
plt.close()

# --------------------------------------------------------------
# 🎯 5. Entrenar modelo final con k óptimo
# --------------------------------------------------------------
kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=10)
cluster_labels = kmeans.fit_predict(X)
df["cluster"] = cluster_labels

# Guardar dataset con cluster asignado
df.to_csv("noticias_con_clusters.csv", index=False)
logging.info("📁 Dataset con clusters guardado en 'noticias_con_clusters.csv'")

# --------------------------------------------------------------
# 🏷️ 6. Palabras clave por cluster
# --------------------------------------------------------------
terms = vectorizer.get_feature_names_out()
cluster_top_terms = {}

for i in range(best_k):
    centroid = kmeans.cluster_centers_[i]
    top_idx = centroid.argsort()[::-1][:15]  # top 15 palabras
    top_terms = [terms[j] for j in top_idx]
    cluster_top_terms[i] = top_terms

# Guardar en txt para revisar
with open("top_terms_por_cluster.txt", "w", encoding="utf-8") as f:
    for cl, palabras in cluster_top_terms.items():
        f.write(f"Cluster {cl}:\n")
        f.write(", ".join(palabras) + "\n\n")

logging.info("📝 Palabras clave por cluster guardadas en 'top_terms_por_cluster.txt'")

# --------------------------------------------------------------
# 📊 7. Tamaño de cada cluster (gráfico)
# --------------------------------------------------------------
cluster_counts = df["cluster"].value_counts().sort_index()
plt.figure(figsize=(6,4))
sns.barplot(x=cluster_counts.index, y=cluster_counts.values)
plt.xlabel("Cluster")
plt.ylabel("Número de noticias")
plt.title("Tamaño de cada cluster")
plt.tight_layout()
plt.savefig("cluster_sizes.png", dpi=300)
plt.close()
logging.info("📊 Gráfico de tamaños de cluster guardado en 'cluster_sizes.png'")

# --------------------------------------------------------------
# 🔗 8. Relación Cluster vs Categoría (si existe)
# --------------------------------------------------------------
if "categoria" in df.columns:
    tabla = pd.crosstab(df["cluster"], df["categoria"])
    tabla.to_csv("cluster_vs_categoria.csv")
    plt.figure(figsize=(10,6))
    sns.heatmap(tabla, annot=False, cmap="Blues")
    plt.xlabel("Categoría original")
    plt.ylabel("Cluster")
    plt.title("Relación entre clusters y categorías originales")
    plt.tight_layout()
    plt.savefig("cluster_vs_categoria_heatmap.png", dpi=300)
    plt.close()
    logging.info("🔥 Mapa de calor cluster vs categoría guardado en 'cluster_vs_categoria_heatmap.png'")
else:
    logging.info("No hay columna 'categoria'; se omite análisis cluster vs categoría.")

# --------------------------------------------------------------
# ✅ 9. Resumen por consola
# --------------------------------------------------------------
print("\n========= RESUMEN CLUSTERING =========")
print(f"Mejor número de clusters (k): {best_k}")
print(f"Silueta promedio: {best_sil:.3f}")
print("\nTamaño de cada cluster:")
print(cluster_counts)

print("\nPalabras clave por cluster (ver archivo 'top_terms_por_cluster.txt'):")
for cl, palabras in cluster_top_terms.items():
    print(f"- Cluster {cl}: {', '.join(palabras[:8])} ...")

print("\n🧾 Archivos generados:")
print("- silhouette_scores.csv")
print("- silhouette_vs_k.png")
print("- noticias_con_clusters.csv")
print("- top_terms_por_cluster.txt")
print("- cluster_sizes.png")
if "categoria" in df.columns:
    print("- cluster_vs_categoria.csv")
    print("- cluster_vs_categoria_heatmap.png")
print("=====================================")
