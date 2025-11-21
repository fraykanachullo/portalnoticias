from db import execute_query

def obtener_noticias_filtradas(fuente, categoria, page, per_page):
    offset = (page - 1) * per_page

    sql = """
        SELECT 
            n.id, n.titulo, n.url_imagen, n.url_noticia,
            n.fecha_publicacion, n.categoria, f.nombre AS fuente
        FROM noticias n
        JOIN fuentes f ON n.fuente_id = f.id
        WHERE (%s = '' OR f.nombre = %s)
          AND (%s = '' OR n.categoria = %s)
        ORDER BY fecha_publicacion DESC
        LIMIT %s OFFSET %s;
    """
    params = (fuente, fuente, categoria, categoria, per_page, offset)
    rows = execute_query(sql, params, fetch=True)

    return {
        "data": rows,
        "page": page,
        "per_page": per_page,
        "count": len(rows)
    }
from db import execute_query

def obtener_portada():
    sql = """
        SELECT n.*, f.nombre AS fuente
        FROM noticias n
        JOIN fuentes f ON n.fuente_id = f.id
        WHERE f.nombre != 'Facebook'
        AND n.url_imagen IS NOT NULL
        ORDER BY COALESCE(n.fecha_publicacion, n.fecha_registro) DESC
        LIMIT 3;
    """
    return execute_query(sql, fetch=True) or []
