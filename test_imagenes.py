from db import execute_query

print("\n🔍 MOSTRANDO LAS ÚLTIMAS 20 IMÁGENES SCRAPEADAS:\n")

rows = execute_query("""
    SELECT id, fuente_id, titulo, url_imagen
    FROM noticias
    ORDER BY id DESC
    LIMIT 20;
""", fetch=True)

for r in rows:
    print(f"[{r['id']}] Fuente {r['fuente_id']}")
    print(f"Título: {r['titulo']}")
    print(f"Imagen: {r['url_imagen']}\n")
