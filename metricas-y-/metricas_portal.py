# ...existing code...
# ==============================================================
# 🧠 Evaluación del Portal de Noticias Inteligente
# Archivo: metrica_portal.py
# Autor: Jhon Alexnader Chambi Vilca
# Fecha: 2025-11-06 (actualizado 2025-11-07)
# ==============================================================

import sys
import os
import logging
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score, roc_curve, auc
)
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, label_binarize
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# --------------------------------------------------------------
# 📁 Cargar y normalizar nombres de columna y datos
# --------------------------------------------------------------
archivo_csv = "noticias02.csv"

def try_read_csv(path):
    # intenta utf-8 y si falla prueba latin1
    try:
        return pd.read_csv(path, encoding="utf-8", quotechar='"', on_bad_lines="skip")
    except Exception:
        try:
            return pd.read_csv(path, encoding="latin1", quotechar='"', on_bad_lines="skip")
        except Exception as e:
            logging.error(f"No se pudo leer el CSV: {e}")
            sys.exit(1)

df = try_read_csv(archivo_csv)

# Normalizar nombres de columnas (quitar espacios, bajar a minúsculas y reemplazar acentos básicos)
def normalize(name: str) -> str:
    s = str(name).strip().lower()
    replace_map = {
        "á":"a", "é":"e", "í":"i", "ó":"o", "ú":"u", "ñ":"n"
    }
    for k,v in replace_map.items():
        s = s.replace(k, v)
    s = s.replace(" ", "_").replace("-", "_")
    return s

orig_columns = list(df.columns)
cols_norm = [normalize(c) for c in orig_columns]

# candidatos para título y categoría
title_candidates = ['titulo', 'title', 'headline', 'titular', 'titulo_noticia', 'titulo_noticia']
cat_candidates = ['categoria', 'categoria_noticia', 'categoria_noticia', 'categoria', 'categoria', 'category', 'label', 'etiqueta']

def find_col(orig_cols, norm_cols, candidates):
    for cand in candidates:
        for orig, norm in zip(orig_cols, norm_cols):
            if norm == cand or cand in norm:
                return orig
    return None

title_col = find_col(orig_columns, cols_norm, title_candidates)
cat_col = find_col(orig_columns, cols_norm, cat_candidates)

if title_col is None or cat_col is None:
    logging.error("No se encontró columna de título o categoría en el CSV.")
    logging.info(f"Columnas detectadas: {orig_columns}")
    logging.info("Asegúrate que el CSV contiene campos similares a 'titulo' y 'categoria'.")
    sys.exit(1)

# Renombrar a nombres esperados por el script
df = df.rename(columns={title_col: "titulo", cat_col: "categoria"})

# Limpiar y filtrar filas con valores nulos en las columnas clave
df["titulo"] = df["titulo"].astype(str).str.strip()
df["categoria"] = df["categoria"].astype(str).str.strip()
df = df.replace({"titulo": {"nan": np.nan}, "categoria": {"nan": np.nan}})
df = df.dropna(subset=["titulo", "categoria"])

if df.empty:
    logging.error("Después de limpiar, no hay filas válidas para procesar.")
    sys.exit(1)

logging.info("✅ Datos cargados y normalizados correctamente.")
logging.info(f"Filas: {len(df)}, Columnas: {list(df.columns)}")
# --------------------------------------------------------------
# 🎯 Variables predictoras y etiqueta
# --------------------------------------------------------------
X = df["titulo"]
y = df["categoria"]

# Convertir etiquetas a numéricas
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# --------------------------------------------------------------
# ⚙️ Stopwords en español: intentar NLTK, fallback a lista interna
# --------------------------------------------------------------
def get_spanish_stopwords():
    try:
        import nltk
        from nltk.corpus import stopwords
        # intenta descargar si no existe (silencioso)
        try:
            sw = set(stopwords.words("spanish"))
        except Exception:
            nltk.download("stopwords", quiet=True)
            sw = set(stopwords.words("spanish"))
        return list(sw)
    except Exception:
        # Lista básica de stopwords en español (fallback)
        return [
            "a","al","algo","algunas","algunos","ante","antes","como","con","contra","cual","cuando",
            "de","del","desde","donde","dos","el","ella","ellas","ellos","en","entre","era","erais",
            "eran","eras","es","esta","estaba","estabais","estaban","estabas","estad","estada",
            "estadas","estados","estados","estais","estamos","estan","estando","estar","estas",
            "este","esto","estos","estoy","fue","fueron","fui","fuimos","ha","hace","haces","hacia",
            "hasta","hay","incluso","la","las","lo","los","me","mi","mis","mucho","muy","ni","no",
            "nos","nosotros","o","os","otra","otros","para","pero","por","porque","que","quien",
            "quienes","se","sea","ser","si","sido","sin","sobre","su","sus","también","tan","tener",
            "tiene","tienen","toda","todas","todo","todos","tu","tus","un","una","uno","unos","usted",
            "vosotros","y","ya"
        ]

spanish_stopwords = get_spanish_stopwords()

# Vectorización de texto (usar lista de stopwords válida)
vectorizer = TfidfVectorizer(stop_words=spanish_stopwords, max_features=3000)
X_vect = vectorizer.fit_transform(X)

# División entrenamiento / prueba (si hay al menos 2 clases)
unique_labels = np.unique(y_encoded)
if len(unique_labels) < 2:
    logging.error("Se necesitan al menos 2 categorías diferentes para entrenar un clasificador.")
    sys.exit(1)

try:
    X_train, X_test, y_train, y_test = train_test_split(
        X_vect, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )
except Exception as e:
    logging.warning(f"No se pudo estratificar al dividir: {e}. Intentando sin estratificación.")
    X_train, X_test, y_train, y_test = train_test_split(
        X_vect, y_encoded, test_size=0.2, random_state=42
    )

# --------------------------------------------------------------
# 🌲 Entrenamiento del modelo
# --------------------------------------------------------------
clf = RandomForestClassifier(n_estimators=200, random_state=42)
clf.fit(X_train, y_train)

# --------------------------------------------------------------
# 📊 Predicciones y métricas
# --------------------------------------------------------------
y_pred = clf.predict(X_test)
y_proba = clf.predict_proba(X_test) if hasattr(clf, "predict_proba") else None

report = classification_report(y_test, y_pred, target_names=label_encoder.classes_, output_dict=True)
df_report = pd.DataFrame(report).transpose()
df_report.to_csv("resultados_metricas.csv", index=True)
logging.info("📊 Resultados guardados en 'resultados_metricas.csv'")

# --------------------------------------------------------------
# 🔢 Matriz de confusión
# --------------------------------------------------------------
matriz = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(8, 6))
sns.heatmap(matriz, annot=True, fmt="d", cmap="Blues", xticklabels=label_encoder.classes_, yticklabels=label_encoder.classes_)
plt.xlabel("Predicción")
plt.ylabel("Real")
plt.title("Matriz de confusión — Portal de Noticias")
plt.tight_layout()
plt.savefig("matriz_confusion.png", dpi=300)
plt.close()
logging.info("Matriz de confusión guardada en 'matriz_confusion.png'")

# --------------------------------------------------------------
# 📈 Gráfico de barras (Precision, Recall, F1)
# --------------------------------------------------------------
# Filtrar solo filas de clases (evitar 'accuracy', 'macro avg' etc.)
class_rows = [c for c in label_encoder.classes_ if c in df_report.index]
metricas_basicas = df_report.loc[class_rows, ["precision", "recall", "f1-score"]]
metricas_basicas.plot(kind="bar", figsize=(10,6))
plt.title("Comparativa de Métricas por Categoría")
plt.xlabel("Categoría")
plt.ylabel("Valor")
plt.ylim(0, 1)
plt.legend(["Precisión", "Recall", "F1-score"])
plt.tight_layout()
plt.savefig("barras_metricas.png", dpi=300)
plt.close()
logging.info("Gráfico de barras guardado en 'barras_metricas.png'")

# --------------------------------------------------------------
# 💎 AUC-ROC (multiclase) — solo si disponemos de probabilidades
# --------------------------------------------------------------
try:
    if y_proba is not None:
        classes_sorted = np.unique(y_encoded)
        y_test_bin = label_binarize(y_test, classes=classes_sorted)
        if y_test_bin.shape[1] == y_proba.shape[1]:
            auc_roc = roc_auc_score(y_test_bin, y_proba, multi_class='ovr')
            logging.info(f"💎 AUC-ROC general: {auc_roc:.3f}")

            # Curvas ROC (solo si pocas clases para legibilidad)
            if y_test_bin.shape[1] <= 5:
                plt.figure(figsize=(7,5))
                for i, clase in enumerate(label_encoder.classes_):
                    fpr, tpr, _ = roc_curve(y_test_bin[:, i], y_proba[:, i])
                    plt.plot(fpr, tpr, label=f"{clase} (AUC={auc(fpr, tpr):.2f})")
                plt.plot([0,1], [0,1], 'k--')
                plt.xlabel("Falsos Positivos")
                plt.ylabel("Verdaderos Positivos")
                plt.title("Curvas ROC por categoría")
                plt.legend()
                plt.tight_layout()
                plt.savefig("roc_curve.png", dpi=300)
                plt.close()
                logging.info("Curvas ROC guardadas en 'roc_curve.png'")
        else:
            logging.warning("Las probabilidades retornadas no coinciden con el número de clases; se omite AUC-ROC.")
    else:
        logging.warning("El clasificador no provee predict_proba; se omite AUC-ROC.")
except Exception as e:
    logging.warning(f"No se pudo calcular AUC-ROC: {e}")

# --------------------------------------------------------------
# ✅ Resumen final en consola
# --------------------------------------------------------------
print("\n========= RESUMEN GENERAL =========")
print(df_report[["precision", "recall", "f1-score"]].head())
print("==================================")
print("🧾 Archivos generados:")
print("- resultados_metricas.csv")
print("- matriz_confusion.png")
print("- barras_metricas.png")
print("- roc_curve.png (si aplica)")
# ...existing code...