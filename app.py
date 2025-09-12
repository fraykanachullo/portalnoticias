from flask import Flask, render_template
import mysql.connector
from datetime import datetime
import threading
import time
import subprocess  # para llamar scraper.py

app = Flask(__name__)

# --------------------
# Conexión a MySQL
# --------------------
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="portal_noticias"
)
cursor = db.cursor(dictionary=True)

# --------------------
# Función para obtener noticias por categoría
# --------------------
def obtener_noticias_por_categoria(categoria):
    sql = """
        SELECT n.titulo, n.subtitulo, n.descripcion, n.url_noticia AS url, n.url_imagen AS imagen_url,
               n.fecha_publicacion, f.nombre AS fuente
        FROM noticias n
        LEFT JOIN fuentes f ON n.fuente_id = f.id
        WHERE n.categoria=%s
        ORDER BY 
            CASE WHEN n.fecha_publicacion IS NOT NULL THEN n.fecha_publicacion ELSE n.fecha_registro END DESC
        LIMIT 10
    """
    cursor.execute(sql, (categoria,))
    return cursor.fetchall()

# --------------------
# Función que llama a scraper.py
# --------------------
def ejecutar_scraper_periodicamente(intervalo_minutos=10):
    while True:
        print(f"[{datetime.now()}] Ejecutando scraper...")
        try:
            # Llama a scraper.py como proceso independiente
            subprocess.run(["python", "scraper.py"], check=True)
            print(f"[{datetime.now()}] Scraper finalizado.")
        except subprocess.CalledProcessError as e:
            print(f"Error al ejecutar scraper: {e}")
        # Espera el tiempo definido
        time.sleep(intervalo_minutos * 60)

# --------------------
# Página principal
# --------------------
@app.route("/")
def index():
    categorias = ["Últimas Noticias", "Política", "Actualidad", "Deportes", "Economía",
                  "Noticias", "Entretenimiento", "Util e Interesante"]
    
    noticias_por_categoria = {}
    for cat in categorias:
        noticias_por_categoria[cat] = obtener_noticias_por_categoria(cat)

    return render_template("index.html", noticias_por_categoria=noticias_por_categoria)

# --------------------
# Main
# --------------------
if __name__ == "__main__":
    # --------------------
    # Crear hilo para scraper
    # --------------------
    scraper_thread = threading.Thread(target=ejecutar_scraper_periodicamente, args=(10,), daemon=True)
    scraper_thread.start()

    # --------------------
    # Ejecutar servidor Flask
    # --------------------
    app.run(debug=True)
