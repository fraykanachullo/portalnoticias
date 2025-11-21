# ============================================================
# 📰 scraper_modular.py — Módulos de scraping de noticias (v6.0 PRO)
# ============================================================

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter, Retry
import feedparser
import logging
import re
import os
from datetime import datetime
from urllib.parse import urljoin

# ------------------------------
# 🧩 Configuración general
# ------------------------------
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    filename=f"logs/scraper_modular_{datetime.now().strftime('%Y-%m-%d')}.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# Configuración global de sesión HTTP
session = requests.Session()
retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
session.mount("http://", HTTPAdapter(max_retries=retries))
session.mount("https://", HTTPAdapter(max_retries=retries))

# ------------------------------
# 🧹 Funciones auxiliares
# ------------------------------
def limpiar_texto(texto):
    """Limpia saltos de línea, espacios, URLs y caracteres especiales."""
    if not texto:
        return ""
    texto = re.sub(r"\s+", " ", texto)
    texto = re.sub(r"http\S+", "", texto)
    texto = texto.replace("\xa0", " ").strip()
    return texto

def extraer_fecha(entry):
    """Devuelve una fecha formateada si está disponible."""
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        try:
            return datetime(*entry.published_parsed[:6])
        except Exception:
            pass
    if hasattr(entry, "published"):
        return entry.published
    return None

# ------------------------------
# 🖼️ EXTRACCIÓN DE IMÁGENES DESDE HTML
# ------------------------------
def extraer_imagen_de_html(url):
    """Extrae imagen principal desde <meta og:image> o el primer <img> grande."""
    try:
        r = session.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=12)
        soup = BeautifulSoup(r.text, "html.parser")

        # Buscar metadatos OG
        og = soup.find("meta", property="og:image")
        if og and og.get("content"):
            return og["content"]

        og2 = soup.find("meta", attrs={"name": "og:image"})
        if og2 and og2.get("content"):
            return og2["content"]

        # Buscar primer IMG grande
        img = soup.find("img")
        if img and img.get("src"):
            return img["src"]

        return ""
    except Exception:
        return ""

# ============================================================
# 🧱 Clase base para scrapers
# ============================================================
class ScraperBase:
    def __init__(self, name, base_url):
        self.name = name
        self.base_url = base_url

    def fetch(self, url):
        """Descarga el HTML de una página y devuelve BeautifulSoup."""
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            r = session.get(url, headers=headers, timeout=15)
            r.raise_for_status()
            return BeautifulSoup(r.text, "html.parser")
        except Exception as e:
            logging.error(f"[{self.name}] Error al obtener {url}: {e}")
            return None

    def parse(self, soup, categoria):
        raise NotImplementedError

    def run(self, categorias, save_func):
        """Ejecución genérica si el medio usa HTML."""
        for nombre, url in categorias.items():
            try:
                soup = self.fetch(url)
                if not soup:
                    continue

                noticias = self.parse(soup, nombre)

                for n in noticias:
                    titulo = limpiar_texto(n.get("titulo"))
                    subtitulo = limpiar_texto(n.get("subtitulo"))
                    descripcion = limpiar_texto(n.get("descripcion"))
                    url_noticia = n.get("url", "")
                    if not url_noticia.startswith("http"):
                        continue

                    img = n.get("img") or extraer_imagen_de_html(url_noticia)

                    save_func(
                        self.name, titulo, nombre, subtitulo, descripcion,
                        url_noticia, img, n.get("fecha")
                    )

            except Exception as e:
                logging.error(f"[{self.name}] Error procesando categoría {nombre}: {e}")
                continue


# ============================================================
# 🧠 SCRAPERS ESPECÍFICOS
# ============================================================

# -------------------
# ✔ RPP Noticias (RSS + IMG)
# -------------------
class RppScraper(ScraperBase):
    def __init__(self):
        super().__init__("RPP", "https://rpp.pe")

    def run(self, categorias, save_func):
        feeds = {"Últimas Noticias": "https://rpp.pe/feed/"}

        for nombre, url in feeds.items():
            feed = feedparser.parse(url)

            for entry in feed.entries:
                fecha = extraer_fecha(entry)
                img = extraer_imagen_de_html(entry.link)

                save_func(
                    self.name,
                    entry.title,
                    nombre,
                    "",
                    getattr(entry, "summary", ""),
                    entry.link,
                    img,
                    fecha
                )

# -------------------
# ✔ América TV (HTML directo)
# -------------------
class AmericaScraper(ScraperBase):
    def __init__(self):
        super().__init__("América TV", "https://www.americatv.com.pe/")

    def run(self, categorias, save_func):
        soup = self.fetch(self.base_url)
        if not soup:
            return

        for art in soup.find_all("article"):
            try:
                h2 = art.find("h2")
                titulo = h2.get_text(strip=True) if h2 else "Sin título"

                enlace = h2.find("a")["href"] if h2 and h2.find("a") else ""
                if enlace and not enlace.startswith("http"):
                    enlace = urljoin(self.base_url, enlace)

                img = ""
                img_tag = art.find("img")
                if img_tag and img_tag.get("src"):
                    img = img_tag["src"]

                if not img:
                    img = extraer_imagen_de_html(enlace)

                save_func(self.name, titulo, "Portada", "", "", enlace, img, None)

            except Exception:
                continue


# -------------------
# ✔ Diario Sin Fronteras (RSS)
# -------------------
class SinFronterasScraper(ScraperBase):
    def __init__(self):
        super().__init__("Diario Sin Fronteras", "https://diariosinfronteras.com.pe")

    def run(self, categorias, save_func):
        feed = feedparser.parse("https://diariosinfronteras.com.pe/feed/")

        for entry in feed.entries:
            fecha = extraer_fecha(entry)
            img = extraer_imagen_de_html(entry.link)

            save_func(
                self.name,
                entry.title,
                "Portada",
                "",
                getattr(entry, "summary", ""),
                entry.link,
                img,
                fecha
            )


# -------------------
# ✔ Perú21 (RSS)
# -------------------
class Peru21ScraperRSS(ScraperBase):
    def __init__(self):
        super().__init__("Perú21", "https://peru21.pe")

    def run(self, categorias, save_func):
        feeds = {
            "Portada": "https://peru21.pe/feed/",
            "Política": "https://peru21.pe/politica/feed/",
            "Economía": "https://peru21.pe/economia/feed/",
            "Deportes": "https://peru21.pe/deportes/feed/",
            "Mundo": "https://peru21.pe/mundo/feed/",
            "Espectáculos": "https://peru21.pe/espectaculos/feed/"
        }

        for nombre, url in feeds.items():
            feed = feedparser.parse(url)
            for entry in feed.entries:
                fecha = extraer_fecha(entry)
                img = extraer_imagen_de_html(entry.link)

                save_func(
                    self.name, entry.title, nombre, "",
                    getattr(entry, "summary", ""), entry.link, img, fecha
                )


# -------------------
# ✔ La República (RSS)
# -------------------
class LrScraperRSS(ScraperBase):
    def __init__(self):
        super().__init__("La República", "https://larepublica.pe")

    def run(self, categorias, save_func):
        feeds = {
            "Portada": "https://larepublica.pe/rss",
            "Política": "https://larepublica.pe/rss/politica",
            "Economía": "https://larepublica.pe/rss/economia",
            "Sociedad": "https://larepublica.pe/rss/sociedad",
            "Mundo": "https://larepublica.pe/rss/mundo",
            "Deportes": "https://larepublica.pe/rss/deportes",
            "Espectáculos": "https://larepublica.pe/rss/espectaculos"
        }

        for nombre, url in feeds.items():
            feed = feedparser.parse(url)

            for entry in feed.entries:
                fecha = extraer_fecha(entry)
                img = extraer_imagen_de_html(entry.link)

                save_func(
                    self.name, entry.title, nombre, "",
                    getattr(entry, "summary", ""), entry.link, img, fecha
                )


# -------------------
# ✔ Andina (RSS + fallback HTML)
# -------------------
class AndinaScraperRSS(ScraperBase):
    def __init__(self):
        super().__init__("Andina", "https://andina.pe")

    def run(self, categorias, save_func):
        feeds = {
            "Portada": "https://andina.pe/rss.aspx",
            "Política": "https://andina.pe/rss.aspx?sec=politica",
            "Economía": "https://andina.pe/rss.aspx?sec=economia",
            "Internacional": "https://andina.pe/rss.aspx?sec=internacional",
        }

        for nombre, url in feeds.items():
            feed = feedparser.parse(url)

            for entry in feed.entries:
                fecha = extraer_fecha(entry)
                img = extraer_imagen_de_html(entry.link)

                save_func(
                    self.name, entry.title, nombre, "",
                    getattr(entry, "summary", ""), entry.link, img, fecha
                )


# -------------------
# ✔ CNN Español (RSS + fallback HTML)
# -------------------
class CnnScraperRSS(ScraperBase):
    def __init__(self):
        super().__init__("CNN Español", "https://cnnespanol.cnn.com")

    def run(self, categorias, save_func):

        feeds = {
            "Portada": "https://cnnespanol.cnn.com/feed/",
            "Mundo": "https://cnnespanol.cnn.com/category/mundo/feed/",
            "Economía": "https://cnnespanol.cnn.com/category/economia/feed/",
            "Deportes": "https://cnnespanol.cnn.com/category/deportes/feed/",
            "Entretenimiento": "https://cnnespanol.cnn.com/category/entretenimiento/feed/"
        }

        for nombre, url in feeds.items():
            try:
                r = session.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
                feed = feedparser.parse(r.text)
            except:
                continue

            for entry in feed.entries:
                fecha = extraer_fecha(entry)
                img = extraer_imagen_de_html(entry.link)

                save_func(
                    self.name, entry.title, nombre, "",
                    getattr(entry, "summary", ""), entry.link, img, fecha
                )
