def obtener_favoritos(user_id):
    sql = "SELECT noticia_id FROM favoritos WHERE user_id = %s"
    return execute_query(sql, (user_id,), fetch=True)

def obtener_historial(user_id):
    sql = "SELECT noticia_id, fecha_visto FROM historial WHERE user_id = %s ORDER BY fecha_visto DESC"
    return execute_query(sql, (user_id,), fetch=True)
