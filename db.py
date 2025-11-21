# ============================================================
# 🧩 db.py — Módulo de conexión MySQL con pool y utilidades
# ============================================================
import mysql.connector
from mysql.connector import pooling
import logging
from datetime import datetime

# ------------------------------------------------------------
# ⚙️ Configuración de logs
# ------------------------------------------------------------
logging.basicConfig(
    filename=f"logs/db_{datetime.now().strftime('%Y-%m-%d')}.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# ------------------------------------------------------------
# 🧠 Configuración del pool de conexiones MySQL
# ------------------------------------------------------------
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "portal_noticias",
    "charset": "utf8mb4",              # soporte completo para emojis, tildes, etc.
    "collation": "utf8mb4_unicode_ci"
}

try:
    connection_pool = pooling.MySQLConnectionPool(
        pool_name="portal_pool",
        pool_size=5,
        **db_config
    )
    logging.info("✅ Pool de conexiones MySQL inicializado correctamente.")
except Exception as e:
    logging.error(f"❌ Error al crear pool de conexiones: {e}")
    raise

# ------------------------------------------------------------
# 🔹 Función general para ejecutar queries
# ------------------------------------------------------------
def execute_query(query, params=None, fetch=False, commit=False):
    """
    Ejecuta una consulta SQL usando el pool de conexiones.

    Parámetros:
        query (str): Consulta SQL a ejecutar.
        params (tuple): Parámetros opcionales para el query.
        fetch (bool): Si True, devuelve los resultados.
        commit (bool): Si True, confirma la transacción.

    Retorna:
        list[dict] o None
    """
    conn = None
    cursor = None
    try:
        conn = connection_pool.get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(query, params or ())

        if commit:
            conn.commit()

        if fetch:
            result = cursor.fetchall()
            return result or []   # Evita devolver None

    except Exception as e:
        logging.error(f"[DB ERROR] {e} | Query: {query}")
        if conn:
            conn.rollback()
        return [] if fetch else None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# ------------------------------------------------------------
# 🔹 Función específica para guardar noticias
# ------------------------------------------------------------
def guardar_noticia(fuente, titulo, categoria, subtitulo, descripcion, url_noticia, url_imagen, fecha_publicacion=None):
    """
    Inserta o actualiza una noticia en la base de datos.

    - Si la fuente no existe, la crea automáticamente.
    - Si la noticia ya existe (mismo URL), actualiza los campos.
    """
    try:
        if not titulo or not url_noticia:
            logging.warning(f"[SKIP] Noticia sin título o URL ({fuente})")
            return

        # Asegurar fecha válida
        if not fecha_publicacion:
            fecha_publicacion = datetime.now()

        # Buscar fuente o crearla si no existe
        fuente_id_query = "SELECT id FROM fuentes WHERE nombre = %s"
        fuente_id_result = execute_query(fuente_id_query, (fuente,), fetch=True)

        if not fuente_id_result:
            insert_fuente = "INSERT INTO fuentes (nombre, url, fecha_registro) VALUES (%s, '', NOW())"
            execute_query(insert_fuente, (fuente,), commit=True)
            fuente_id_result = execute_query(fuente_id_query, (fuente,), fetch=True)

        fuente_id = fuente_id_result[0]["id"]

        # Insertar o actualizar noticia
        sql = """
            INSERT INTO noticias (
                fuente_id, titulo, categoria, subtitulo, descripcion,
                url_noticia, url_imagen, fecha_publicacion, fecha_registro
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
            ON DUPLICATE KEY UPDATE
                subtitulo = VALUES(subtitulo),
                descripcion = VALUES(descripcion),
                url_imagen = VALUES(url_imagen),
                fecha_publicacion = VALUES(fecha_publicacion),
                fecha_registro = NOW()
        """

        execute_query(
            sql,
            (
                fuente_id,
                titulo[:255],
                categoria or "General",
                subtitulo or "",
                descripcion or "",
                url_noticia,
                url_imagen or "",
                fecha_publicacion
            ),
            commit=True
        )

        logging.info(f"[OK] Guardada noticia de {fuente}: {titulo[:80]}")

    except Exception as e:
        logging.error(f"[ERROR] No se pudo guardar noticia ({fuente}): {e}")
