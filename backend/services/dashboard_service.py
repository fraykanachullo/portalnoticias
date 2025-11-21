# ============================================================
# 📊 dashboard_service.py — Servicios Panel Usuario (PRO 2025)
# ============================================================

from db import execute_query
from datetime import datetime, timedelta


# ============================================================
# 1️⃣ ESTADÍSTICAS GENERALES
# ============================================================
def obtener_estadisticas_generales():
    """
    Retorna estadísticas básicas del portal:
    - Total de noticias
    - Total de fuentes
    - Total de categorías
    """

    sql = """
        SELECT 
            COUNT(*) AS total_noticias,
            COUNT(DISTINCT fuente_id) AS total_fuentes,
            COUNT(DISTINCT categoria) AS total_categorias
        FROM noticias;
    """

    result = execute_query(sql, fetch=True)
    return result[0] if result else {
        "total_noticias": 0,
        "total_fuentes": 0,
        "total_categorias": 0
    }


# ============================================================
# 2️⃣ ÚLTIMAS NOTICIAS (20 más recientes)
# ============================================================
def obtener_ultimas_noticias(limit=20):
    """
    Devuelve las noticias más recientes para mostrar en el panel.
    """

    sql = """
        SELECT 
            n.id,
            n.titulo,
            n.descripcion,
            n.url_imagen,
            n.url_noticia,
            n.categoria,
            n.fecha_publicacion,
            f.nombre AS fuente
        FROM noticias n
        JOIN fuentes f ON n.fuente_id = f.id
        WHERE n.url_noticia IS NOT NULL
        ORDER BY COALESCE(n.fecha_publicacion, n.fecha_registro) DESC
        LIMIT %s;
    """

    data = execute_query(sql, (limit,), fetch=True)
    return data or []


# ============================================================
# 3️⃣ ANÁLISIS DE SENTIMIENTO
# ============================================================
def obtener_sentimiento_general():
    """
    Análisis simple de sentimiento basado en palabras clave.
    Retorna: {"positivos": X, "negativos": Y, "neutros": Z}
    """

    positivos = [
        "bueno", "mejora", "éxito", "logra", "ganó", "positivo",
        "avance", "crece", "récord", "beneficio", "ganancia", "progreso",
        "victoria", "éxito", "potencial", "crecimiento"
    ]

    negativos = [
        "malo", "crisis", "muere", "caída", "pérdida", "negativo",
        "accidente", "corrupción", "protesta", "denuncia", "fracaso",
        "problema", "riesgo", "amenaza", "desastre", "tragedia"
    ]

    sql = """
        SELECT titulo, descripcion
        FROM noticias
        ORDER BY COALESCE(fecha_publicacion, fecha_registro) DESC
        LIMIT 300;
    """

    rows = execute_query(sql, fetch=True) or []

    def score(texto):
        text = texto.lower()
        return sum(p in text for p in positivos) - sum(n in text for n in negativos)

    pos = neg = neu = 0

    for row in rows:
        text = f"{row.get('titulo', '')} {row.get('descripcion', '')}"
        s = score(text)

        if s > 0:
            pos += 1
        elif s < 0:
            neg += 1
        else:
            neu += 1

    return {
        "positivos": pos,
        "negativos": neg,
        "neutros": neu
    }


# ============================================================
# 4️⃣ NOTICIAS HOY
# ============================================================
def obtener_noticias_hoy():
    """
    Retorna la cantidad de noticias publicadas hoy.
    """

    sql = """
        SELECT COUNT(*) AS total
        FROM noticias
        WHERE DATE(COALESCE(fecha_publicacion, fecha_registro)) = CURDATE();
    """

    result = execute_query(sql, fetch=True)
    return result[0]["total"] if result else 0


# ============================================================
# 5️⃣ CATEGORÍAS MÁS ACTIVAS
# ============================================================
def obtener_categorias_activas(limit=5):
    """
    Retorna las categorías con más noticias.
    """

    sql = """
        SELECT 
            COALESCE(categoria, 'Sin categoría') AS categoria,
            COUNT(*) AS total
        FROM noticias
        GROUP BY categoria
        ORDER BY total DESC
        LIMIT %s;
    """

    data = execute_query(sql, (limit,), fetch=True)
    return data or []


# ============================================================
# 6️⃣ FUENTES MÁS ACTIVAS
# ============================================================
def obtener_fuentes_activas(limit=5):
    """
    Retorna las fuentes con más noticias.
    """

    sql = """
        SELECT 
            f.nombre AS fuente,
            COUNT(*) AS total
        FROM noticias n
        JOIN fuentes f ON n.fuente_id = f.id
        GROUP BY f.nombre
        ORDER BY total DESC
        LIMIT %s;
    """

    data = execute_query(sql, (limit,), fetch=True)
    return data or []


# ============================================================
# 7️⃣ NOTICIAS POR CATEGORÍA (ÚLTIMOS 7 DÍAS)
# ============================================================
def obtener_noticias_por_categoria_recientes():
    """
    Retorna la distribución de noticias por categoría
    en los últimos 7 días.
    """

    sql = """
        SELECT 
            COALESCE(categoria, 'Sin categoría') AS categoria,
            COUNT(*) AS total
        FROM noticias
        WHERE COALESCE(fecha_publicacion, fecha_registro) >= CURDATE() - INTERVAL 7 DAY
        GROUP BY categoria
        ORDER BY total DESC;
    """

    data = execute_query(sql, fetch=True)
    return data or []


# ============================================================
# 8️⃣ INFORMACIÓN DE USUARIO
# ============================================================
def obtener_info_usuario(user_id):
    """
    Obtiene la información del usuario autenticado.
    """

    sql = "SELECT id, nombre, email, rol, fecha_registro FROM usuarios WHERE id = %s"
    result = execute_query(sql, (user_id,), fetch=True)
    return result[0] if result else None


# ============================================================
# 9️⃣ RESUMEN DEL PANEL (TODA LA INFO)
# ============================================================
def obtener_resumen_completo(user_id):
    """
    Retorna un resumen completo para el dashboard del usuario.
    """

    return {
        "usuario": obtener_info_usuario(user_id),
        "estadisticas": obtener_estadisticas_generales(),
        "sentimiento": obtener_sentimiento_general(),
        "noticias_hoy": obtener_noticias_hoy(),
        "categorias_activas": obtener_categorias_activas(),
        "fuentes_activas": obtener_fuentes_activas(),
        "ultimas_noticias": obtener_ultimas_noticias(20)
    }




    