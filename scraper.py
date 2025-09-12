from bs4 import BeautifulSoup
import requests
import re
import mysql.connector
from datetime import datetime

# --------------------
# Conexión a MySQL
# --------------------
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",  # tu contraseña
    database="portal_noticias"
)
cursor = db.cursor()

# --------------------
# Funciones de DB
# --------------------
def obtener_id_fuente(nombre_fuente):
    cursor.execute("SELECT id FROM fuentes WHERE nombre=%s", (nombre_fuente,))
    resultado = cursor.fetchone()
    return resultado[0] if resultado else None

def guardar_noticia(fuente, titulo, categoria, subtitulo, descripcion, url_noticia, url_imagen, fecha_publicacion=None):
    fuente_id = obtener_id_fuente(fuente)
    if not fuente_id:
        print(f"Fuente {fuente} no encontrada.")
        return
    try:
        sql = """
        INSERT INTO noticias (fuente_id, titulo, categoria, subtitulo, descripcion, url_noticia, url_imagen, fecha_publicacion)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            subtitulo=VALUES(subtitulo),
            descripcion=VALUES(descripcion),
            url_imagen=VALUES(url_imagen),
            fecha_publicacion=VALUES(fecha_publicacion),
            fecha_registro=CURRENT_TIMESTAMP
        """
        cursor.execute(sql, (fuente_id, titulo, categoria, subtitulo, descripcion, url_noticia, url_imagen, fecha_publicacion))
        db.commit()
        print(f"Noticia guardada: {titulo}")
    except Exception as e:
        print(f"Error al guardar noticia: {e}")

# --------------------
# Función para limpiar nombre
# --------------------
def limpiar_nombre(nombre):
    nombre = re.sub(r'[\\/*?:"<>|]', "", nombre).strip()
    return nombre[:50] if len(nombre) > 50 else nombre

# --------------------
# Scraping RPP (preciso)
# --------------------
def scrape_rpp(categoria_url, categoria_nombre):
    try:
        response = requests.get(categoria_url, timeout=10)
        response.raise_for_status()
    except:
        print(f"No se pudo acceder a {categoria_url}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    base_url = "https://rpp.pe"

    articulos = soup.find_all('article')
    for art in articulos:
        # Título
        h1 = art.find(['h1','h2'])
        titulo = h1.get_text(strip=True) if h1 else 'No hay título'

        # Enlace
        a_tag = art.find('a')
        url_noticia = base_url + a_tag['href'] if a_tag and a_tag.get('href') else 'No hay enlace'

        # Subtítulo
        h3 = art.find('h3')
        subtitulo = h3.get_text(strip=True) if h3 else 'No hay subtítulo disponible'

        # Descripción (primer <p> con texto válido dentro del article)
        descripcion = 'No hay descripción'
        p_tags = art.select("div > p")  # <-- usa select para ir directo al <p> dentro del div
        for p in p_tags:
            texto = p.get_text(strip=True)
            if texto:
                descripcion = texto
                break

        # Imagen
        img_tag = art.find('img')
        url_imagen = img_tag['src'] if img_tag and img_tag.get('src') else ''

        # Fecha de publicación
        fecha_publicacion = None
        time_tag = art.find('time')
        if time_tag and time_tag.get('datetime'):
            try:
                fecha_publicacion = datetime.fromisoformat(time_tag['datetime'].replace('Z','+00:00'))
            except:
                pass

        # Guardar noticia
        guardar_noticia("RPP", titulo, categoria_nombre, subtitulo, descripcion, url_noticia, url_imagen, fecha_publicacion)

# --------------------
# Scraping America TV
# --------------------
def scrape_america(categoria_url, categoria_nombre):
    try:
        response = requests.get(categoria_url, timeout=10)
        response.raise_for_status()
    except:
        print(f"No se pudo acceder a {categoria_url}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    base_url = "https://www.americatv.com.pe"

    titulos = soup.find_all('h2')
    for titulo_tag in titulos:
        titulo = titulo_tag.get_text(strip=True)
        enlace_tag = titulo_tag.find('a')
        if not enlace_tag:
            parent_article = titulo_tag.find_parent('article')
            if parent_article:
                enlace_tag = parent_article.find('a')
        url_noticia = base_url + enlace_tag['href'] if enlace_tag else 'No hay enlace'

        subtitulo_tag = titulo_tag.find_next('h3')
        subtitulo = subtitulo_tag.get_text(strip=True) if subtitulo_tag else 'No hay subtítulo disponible'

        descripcion_tag = titulo_tag.find_next('p')
        descripcion = descripcion_tag.get_text(strip=True) if descripcion_tag else 'No hay descripción disponible'

        img_tag = titulo_tag.find_next('img')
        url_imagen = img_tag['src'] if img_tag else ''

        fecha_publicacion = None
        time_tag = titulo_tag.find_next('time')
        if time_tag and time_tag.get('datetime'):
            try:
                fecha_publicacion = datetime.fromisoformat(time_tag['datetime'].replace('Z','+00:00'))
            except:
                pass

        guardar_noticia("America TV", titulo, categoria_nombre, subtitulo, descripcion, url_noticia, url_imagen, fecha_publicacion)

# --------------------
# Ejecutar scraping
# --------------------
def main():
    print("Iniciando scraping de noticias...")

    categorias_rpp = {
        "Últimas Noticias": "https://rpp.pe/ultimas-noticias",
        "Política": "https://rpp.pe/politica",
        "Actualidad": "https://rpp.pe/actualidad",
        "Deportes": "https://rpp.pe/deportes",
        "Economía": "https://rpp.pe/economia"
    }

    categorias_america = {
        "Noticias": "https://www.americatv.com.pe/noticias",
        "Deportes": "https://www.americatv.com.pe/deportes",
        "Entretenimiento": "https://www.americatv.com.pe/entretenimiento",
        "Util e Interesante": "https://www.americatv.com.pe/util-e-interesante"
    }

    for nombre, url in categorias_rpp.items():
        scrape_rpp(url, nombre)

    for nombre, url in categorias_america.items():
        scrape_america(url, nombre)

    print("Scraping finalizado.")

if __name__ == "__main__":
    main()
