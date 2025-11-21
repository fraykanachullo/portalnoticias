# backend/services/sentimiento_service.py

from db import execute_query

# Palabras clave simples para detección aproximada
POSITIVAS = ["bueno", "excelente", "positivo", "éxito", "logro", "avance", "mejora"]
NEGATIVAS = ["malo", "crisis", "negativo", "caída", "peligro", "tragedia", "problema"]

def analizar_sentimiento_texto(texto):
    """
    Analiza un texto muy simple basado en conteo de palabras clave.
    Retorna "pos", "neg" o "neu".
    """

    texto = texto.lower()

    score_pos = sum(1 for w in POSITIVAS if w in texto)
    score_neg = sum(1 for w in NEGATIVAS if w in texto)

    if score_pos > score_neg:
        return "pos"
    elif score_neg > score_pos:
        return "neg"
    else:
        return "neu"


def obtener_sentimientos():
    """
    Recorre TODAS las noticias y devuelve:
    { "pos": X, "neg": Y, "neu": Z }
    """

    noticias = execute_query("""
        SELECT titulo, descripcion
        FROM noticias
        ORDER BY id DESC
        LIMIT 200;
    """, fetch=True)

    pos = neg = neu = 0

    if not noticias:
        return {"pos": 0, "neg": 0, "neu": 0}

    for n in noticias:
        texto = f"{n.get('titulo', '')} {n.get('descripcion', '')}"
        sentimiento = analizar_sentimiento_texto(texto)

        if sentimiento == "pos":
            pos += 1
        elif sentimiento == "neg":
            neg += 1
        else:
            neu += 1

    return {"pos": pos, "neg": neg, "neu": neu}
