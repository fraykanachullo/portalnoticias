from facebook_scraper import get_posts
from datetime import datetime

print("=== Prueba rápida de Facebook (con cookies) ===")

try:
    count = 0
    for post in get_posts('RPPNoticias', pages=2, extra_info=True, cookies='cookies.txt', options={"comments": False}):
        contenido = post.get("text", "").strip()
        if not contenido:
            continue
        print(f"\n📰 {contenido[:120]}...")
        print(f"URL: {post.get('post_url', '')}")
        print(f"Fecha: {post.get('time', datetime.now())}")
        count += 1
    print(f"\n✅ Total publicaciones: {count}")
except Exception as e:
    print(f"❌ Error: {e}")
