# ============================================================
# 📘 FACEBOOK SCRAPER (v3.0 — Selenium + MySQL Integration)
# ============================================================

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from datetime import datetime
import logging
import os
import time

# Importar función para guardar en la BD
from db import guardar_noticia

# ------------------------------------------------------------
# 🧩 Configuración de logging
# ------------------------------------------------------------
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename=f"logs/facebook_selenium_{datetime.now().strftime('%Y-%m-%d')}.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# ------------------------------------------------------------
# ⚙️ Configuración general de Selenium
# ------------------------------------------------------------
def iniciar_driver():
    options = Options()
    options.add_argument("--headless=new")      # sin interfaz gráfica
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--lang=en-US")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# ------------------------------------------------------------
# 🚀 Scraper de publicaciones
# ------------------------------------------------------------
def run_facebook_scraper(save_func=guardar_noticia):
    paginas = {
        "RPP Noticias": "https://www.facebook.com/RPPNoticias",
        "América Televisión": "https://www.facebook.com/AmericaTelevision",
        "La República": "https://www.facebook.com/larepublica.pe",
    }

    driver = iniciar_driver()
    total_guardadas = 0

    for nombre, url in paginas.items():
        try:
            print(f"[FACEBOOK] 🔍 Analizando página: {nombre}")
            driver.get(url)
            time.sleep(5)  # dejar cargar el contenido

            # Hacer scroll para cargar más publicaciones
            for _ in range(3):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)

            # Extraer HTML
            soup = BeautifulSoup(driver.page_source, "html.parser")
            articulos = soup.find_all("div", attrs={"role": "article"})

            print(f"[FACEBOOK] {nombre}: {len(articulos)} publicaciones detectadas.")
            logging.info(f"[FACEBOOK] {nombre}: {len(articulos)} publicaciones detectadas.")

            for art in articulos[:10]:  # limitar para evitar spam
                try:
                    texto = art.get_text(" ", strip=True)
                    if not texto or len(texto) < 50:
                        continue

                    enlaces = art.find_all("a", href=True)
                    post_url = ""
                    for a in enlaces:
                        if "posts" in a["href"] or "videos" in a["href"]:
                            post_url = a["href"]
                            break

                    # Guardar
                    save_func(
                        "Facebook",
                        texto[:90] + "...",
                        "Publicación",
                        "",
                        texto,
                        post_url,
                        "",
                        datetime.now()
                    )
                    total_guardadas += 1

                except Exception as e:
                    logging.error(f"[FACEBOOK] Error procesando post: {e}")
                    continue

        except Exception as e:
            print(f"❌ Error en {nombre}: {e}")
            logging.error(f"[FACEBOOK] {nombre} falló: {e}")

    driver.quit()
    print(f"✅ Facebook scraping completado ({total_guardadas} publicaciones guardadas)")
    logging.info(f"✅ Total guardadas: {total_guardadas}")

# ------------------------------------------------------------
# 🧪 Test manual
# ------------------------------------------------------------
if __name__ == "__main__":
    run_facebook_scraper()
