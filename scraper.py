# ============================================================
# 🧠 scraper.py — Coordinador principal de scrapers (v5.0)
# ============================================================

from scraper_modular import (
    RppScraper,
    AmericaScraper,
    SinFronterasScraper,
    Peru21ScraperRSS,
    LrScraperRSS,
    AndinaScraperRSS,
    CnnScraperRSS
)
from facebook_scraper_modular import run_facebook_scraper
from db import guardar_noticia

import logging
import schedule
import time
from datetime import datetime
import os
import traceback

# ============================================================
# ⚙️ CONFIGURACIÓN DE LOGS
# ============================================================
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    filename=f"logs/scraper_main_{datetime.now().strftime('%Y-%m-%d')}.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# ============================================================
# 🚀 FUNCIÓN PRINCIPAL
# ============================================================
def main():
    print("🚀 Iniciando scraping general de fuentes...")
    logging.info("=== INICIO DE SCRAPING GENERAL ===")

    # --- Lista de scrapers de medios ---
    scrapers = [
        RppScraper(),
        AmericaScraper(),
        SinFronterasScraper(),
        Peru21ScraperRSS(),
        LrScraperRSS(),
        AndinaScraperRSS(),
        CnnScraperRSS()
    ]

    total_fuentes = len(scrapers)
    total_procesadas = 0
    errores = 0

    # --- Ejecutar cada scraper ---
    for scraper in scrapers:
        try:
            logging.info(f"[SCRAPER] Iniciando: {scraper.name}")
            print(f"🔹 Procesando: {scraper.name}")
            scraper.run({}, guardar_noticia)
            total_procesadas += 1
        except Exception as e:
            errores += 1
            logging.error(f"[ERROR] {scraper.name}: {e}\n{traceback.format_exc()}")
            print(f"❌ Error en {scraper.name}: {e}")

    # --- Integración con Facebook ---
    try:
        print("📘 Iniciando extracción de publicaciones de Facebook...")
        logging.info("[FACEBOOK] Iniciando extracción de publicaciones...")
        run_facebook_scraper(guardar_noticia)
        logging.info("[FACEBOOK] Extracción completada correctamente.")
        print("✅ Facebook scraping completado.")
    except Exception as e:
        errores += 1
        logging.error(f"[ERROR] Facebook scraper: {e}\n{traceback.format_exc()}")
        print(f"❌ Error en Facebook scraper: {e}")

    # --- Resumen ---
    resumen = (
        f"✅ Scraping finalizado. {total_procesadas}/{total_fuentes} fuentes procesadas, "
        f"{errores} errores."
    )
    print(resumen)
    logging.info(resumen)
    logging.info("=== FIN DE SCRAPING ===\n")

# ============================================================
# ⏱️ PROGRAMADOR AUTOMÁTICO
# ============================================================
def ejecutar_scraping_periodico():
    """
    Programa el scraping automático cada 3 horas.
    """
    schedule.every(3).hours.do(main)
    print("⏱ Ejecutando scraping automático cada 3 horas... (Ctrl + C para detener)")
    logging.info("⏱ Scraper programado cada 3 horas.")

    while True:
        schedule.run_pending()
        time.sleep(60)

# ============================================================
# 🧪 MAIN
# ============================================================
if __name__ == "__main__":
    main()
