import requests

def validar_imagen(url: str) -> str:
    """Verifica si una imagen existe. Si no, devuelve un placeholder."""
    if not url:
        return ""
    
    try:
        r = requests.head(url, timeout=3)
        if r.status_code == 200 and "image" in r.headers.get("Content-Type", ""):
            return url
    except:
        pass

    return ""   # forzar fallback
