# backend/services/estadisticas_service.py

from db import execute_query


# ======================================================
#   📌 TOP 10 NOTICIAS RECIENTES
# ======================================================
def top_noticias(limit=10):
    """
    Devuelve las noticias más recientes para el ranking del panel IA.
    """

    sql = f"""
        SELECT 
            n.id, n.titulo, n.categoria,
            COALESCE(n.fecha_publicacion, n.fecha_registro) AS fecha_publicacion,
            f.nombre AS fuente
        FROM noticias n
        JOIN fuentes f ON n.fuente_id = f.id
        ORDER BY fecha_publicacion DESC
        LIMIT %s;
    """

    data = execute_query(sql, (limit,), fetch=True)

    return data or []
