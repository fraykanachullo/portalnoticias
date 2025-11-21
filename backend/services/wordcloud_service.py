# ============================================================
# WordCloud Service — PRO 2025 (PNG HD + Limpieza Inteligente)
# ============================================================

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
from wordcloud import WordCloud
from io import BytesIO
from db import execute_query
import re


# ============================================================
# 🔹 Limpieza Inteligente de Texto (NLP Light)
# ============================================================

def limpiar_texto(texto: str):
    if not texto:
        return ""

    t = texto.lower()

    # ---- Eliminar URLs ----
    t = re.sub(r"http\S+", " ", t)
    t = re.sub(r"www\S+", " ", t)

    # ---- Basura de noticias / medios ----
    t = re.sub(r"\b(pe|com|net|org|html|amp|video|portada|noticias|rpp|youtube|img)\b", " ", t)

    # ---- Quitar símbolos y números ----
    t = re.sub(r"[^a-záéíóúñü\s]", " ", t)

    # ---- Stopwords PRO LATAM ----
    stopwords = set("""
        de la los las un una unos unas que por para con sin del al en y o u
        es son fue ser se ya más muy pero como sobre entre esto esta estas estos
        así aún solo siempre nunca cada hacia haber siendo estaba están mismo misma
        donde cuando porque entonces luego antes después durante tras dentro fuera
        peru lima rpp mundo última ultimo ultimas ultimos
        portada video imagen fotos foto ver vivo directo
        cuenta verified share shares account comentario comentarios public publico
        internacional nacional regional diario peruana peruano politica política
        deportes futbol fútbol club seleccion peru
        """.split())

    palabras = [
        p for p in t.split()
        if len(p) > 3 and p not in stopwords
    ]

    return " ".join(palabras)


# ============================================================
# 🔹 Generar WordCloud (PNG HD)
# ============================================================

def generar_wordcloud(texto: str = None):
    """
    Si viene texto directo → se limpia y genera nube.
    Si no viene texto → se extrae desde BD los últimos 400 títulos/descripciones.
    """

    if texto and texto.strip():
        texto_final = limpiar_texto(texto)
    else:
        rows = execute_query("""
            SELECT titulo, descripcion
            FROM noticias
            ORDER BY COALESCE(fecha_publicacion, fecha_registro) DESC
            LIMIT 400;
        """, fetch=True)

        if not rows:
            return None

        texto_bruto = " ".join(
            (r.get("titulo") or "") + " " + (r.get("descripcion") or "")
            for r in rows
        )

        texto_final = limpiar_texto(texto_bruto)

        if not texto_final.strip():
            return None

    wc = WordCloud(
        width=1400,
        height=700,
        background_color="white",
        prefer_horizontal=0.9,
        colormap="viridis",
        max_words=100,
        collocations=False
    ).generate(texto_final)

    img = BytesIO()
    plt.figure(figsize=(14, 7), dpi=120)
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.savefig(img, format="png", bbox_inches="tight", pad_inches=0)
    plt.close()

    img.seek(0)
    return img
