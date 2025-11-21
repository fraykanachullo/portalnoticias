# ============================================================
# API ROUTES — Panel IA + Noticias + Estadísticas + Notificaciones (PRO 2025)
# ============================================================

from flask import Blueprint, request, jsonify, Response, session, current_app
from db import execute_query
from collections import Counter
from backend.services.wordcloud_service import generar_wordcloud, limpiar_texto

api_bp = Blueprint("api", __name__, url_prefix="/api")

# ============================================================
# 🔹 1. NOTICIAS (PAGINACIÓN + FILTROS)
# ============================================================

@api_bp.get("/noticias")
def api_noticias():
    fuente = request.args.get("fuente", "").strip()
    categoria = request.args.get("categoria", "").strip()
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 12))

    offset = (page - 1) * per_page

    sql = """
        SELECT 
            n.id, n.titulo, n.url_imagen, n.url_noticia,
            n.categoria, n.fecha_publicacion,
            f.nombre AS fuente
        FROM noticias n
        JOIN fuentes f ON n.fuente_id = f.id
        WHERE (%s = '' OR f.nombre = %s)
        AND (%s = '' OR n.categoria = %s)
        ORDER BY COALESCE(n.fecha_publicacion, n.fecha_registro) DESC
        LIMIT %s OFFSET %s;
    """
    params = (fuente, fuente, categoria, categoria, per_page, offset)
    data = execute_query(sql, params, fetch=True)

    return jsonify({
        "page": page,
        "per_page": per_page,
        "total": len(data),
        "data": data
    })


# ============================================================
# 🔹 2. NOTICIAS SOLO FACEBOOK
# ============================================================

@api_bp.get("/facebook")
def api_facebook():
    limit = int(request.args.get("limit", 6))

    sql = """
        SELECT 
            n.titulo, n.descripcion, n.url_imagen,
            n.url_noticia AS url, n.fecha_publicacion
        FROM noticias n
        JOIN fuentes f ON n.fuente_id = f.id
        WHERE f.nombre = 'Facebook'
        ORDER BY COALESCE(n.fecha_publicacion, n.fecha_registro) DESC
        LIMIT %s;
    """
    data = execute_query(sql, (limit,), fetch=True)
    return jsonify(data)


# ============================================================
# 🔹 3. ESTADÍSTICAS GENERALES
# ============================================================

@api_bp.get("/stats/general")
def api_stats_general():
    sql = """
        SELECT 
            COUNT(*) AS total_noticias,
            COUNT(DISTINCT fuente_id) AS total_fuentes,
            COUNT(DISTINCT categoria) AS total_categorias
        FROM noticias;
    """
    data = execute_query(sql, fetch=True)[0]
    return jsonify(data)


# ============================================================
# 🔹 4. CATEGORÍAS
# ============================================================

@api_bp.get("/stats/categorias")
def api_stats_categorias():
    rows = execute_query("""
        SELECT COALESCE(categoria, 'Sin categoría') AS categoria,
               COUNT(*) AS total
        FROM noticias
        GROUP BY categoria
        ORDER BY total DESC;
    """, fetch=True) or []
    return jsonify(rows)


# ============================================================
# 🔹 5. FUENTES
# ============================================================

@api_bp.get("/stats/fuentes")
def api_stats_fuentes():
    rows = execute_query("""
        SELECT f.nombre AS fuente,
               COUNT(*) AS total
        FROM noticias n
        JOIN fuentes f ON n.fuente_id = f.id
        GROUP BY f.nombre
        ORDER BY total DESC;
    """, fetch=True) or []
    return jsonify(rows)


# ============================================================
# 🔹 6. ANÁLISIS DE SENTIMIENTO BÁSICO
# ============================================================

@api_bp.get("/stats/sentimiento")
def api_stats_sentimiento():

    sql = """
        SELECT titulo, descripcion
        FROM noticias
        ORDER BY COALESCE(fecha_publicacion, fecha_registro) DESC
        LIMIT 300;
    """
    rows = execute_query(sql, fetch=True) or []

    positivos_palabras = ["bueno", "mejora", "éxito", "logra", "ganó", "positivo", "avance", "crece", "récord", "beneficio"]
    negativos_palabras = ["malo", "crisis", "muere", "caída", "pérdida", "negativo", "accidente", "corrupción", "protesta", "denuncia"]

    def score(texto):
        text = texto.lower()
        return sum(p in text for p in positivos_palabras) - sum(n in text for n in negativos_palabras)

    pos = neg = neu = 0

    for r in rows:
        text = f"{r.get('titulo','')} {r.get('descripcion','')}"
        s = score(text)

        if s > 0:
            pos += 1
        elif s < 0:
            neg += 1
        else:
            neu += 1

    return jsonify({"positivos": pos, "negativos": neg, "neutros": neu})


# ============================================================
# 🔹 7. WORDCLOUD JSON CON FILTROS PRO
# ============================================================

@api_bp.get("/stats/wordcloud")
def api_stats_wordcloud():

    categoria = request.args.get("categoria", "").strip()
    fuente = request.args.get("fuente", "").strip()
    dias = request.args.get("dias", "").strip()
    query = (request.args.get("q", "") or request.args.get("query", "")).strip()

    sql = """
        SELECT n.titulo, n.descripcion
        FROM noticias n
        JOIN fuentes f ON n.fuente_id = f.id
    """

    filtros = []
    params = []

    if categoria:
        filtros.append("n.categoria = %s")
        params.append(categoria)

    if fuente:
        filtros.append("f.nombre = %s")
        params.append(fuente)

    if dias:
        try:
            num = int(dias)
            if 0 < num <= 365:
                filtros.append(
                    f"COALESCE(n.fecha_publicacion, n.fecha_registro) >= NOW() - INTERVAL {num} DAY"
                )
        except:
            pass

    if query:
        filtros.append("(n.titulo LIKE %s OR n.descripcion LIKE %s)")
        like = f"%{query}%"
        params.extend([like, like])

    if filtros:
        sql += " WHERE " + " AND ".join(filtros)

    sql += """
        ORDER BY COALESCE(n.fecha_publicacion, n.fecha_registro) DESC
        LIMIT 500;
    """

    rows = execute_query(sql, tuple(params), fetch=True) or []

    texto_bruto = " ".join(
        f"{r.get('titulo', '')} {r.get('descripcion', '')}"
        for r in rows
    )

    texto_limpio = limpiar_texto(texto_bruto)
    if not texto_limpio.strip():
        return jsonify([])

    palabras = texto_limpio.split()
    conteo = Counter(palabras).most_common(80)

    return jsonify([
        {"text": palabra, "value": int(freq)}
        for palabra, freq in conteo
    ])


# ============================================================
# 🔹 8. WORDCLOUD IMAGEN (PNG) CON FILTROS
# ============================================================

@api_bp.get("/stats/wordcloud_image")
def api_wordcloud_image():

    categoria = request.args.get("categoria", "").strip()
    fuente = request.args.get("fuente", "").strip()
    dias = request.args.get("dias", "").strip()
    query = (request.args.get("q", "") or request.args.get("query", "")).strip()

    sql = """
        SELECT n.titulo, n.descripcion
        FROM noticias n
        JOIN fuentes f ON n.fuente_id = f.id
    """

    filtros = []
    params = []

    if categoria:
        filtros.append("n.categoria = %s")
        params.append(categoria)

    if fuente:
        filtros.append("f.nombre = %s")
        params.append(fuente)

    if dias:
        try:
            num = int(dias)
            if 0 < num <= 365:
                filtros.append(
                    f"COALESCE(n.fecha_publicacion, n.fecha_registro) >= NOW() - INTERVAL {num} DAY"
                )
        except:
            pass

    if query:
        filtros.append("(n.titulo LIKE %s OR n.descripcion LIKE %s)")
        like = f"%{query}%"
        params.extend([like, like])

    if filtros:
        sql += " WHERE " + " AND ".join(filtros)

    sql += """
        ORDER BY COALESCE(n.fecha_publicacion, n.fecha_registro) DESC
        LIMIT 500;
    """

    rows = execute_query(sql, tuple(params), fetch=True) or []

    texto = " ".join(
        f"{r.get('titulo','')} {r.get('descripcion','')}"
        for r in rows
    )

    if not texto.strip():
        return "", 204

    img = generar_wordcloud(texto)
    if not img:
        return "", 204

    return Response(img.getvalue(), mimetype="image/png")


# ============================================================
# 🔹 9. ALERTAS IA (RIESGOS)
# ============================================================

@api_bp.get("/stats/alertas")
def api_stats_alertas():

    palabras_riesgo = [
        "muerte", "asesinato", "homicidio", "violación", "abuso",
        "tragedia", "accidente", "choque", "heridos", "incendio",
        "corrupción", "robo", "asalto", "crimen", "secuestro",
        "desastre", "protesta", "enfrentamiento"
    ]

    rows = execute_query("""
        SELECT 
            n.id, n.titulo, n.descripcion, n.categoria,
            COALESCE(n.fecha_publicacion, n.fecha_registro) AS fecha,
            f.nombre AS fuente
        FROM noticias n
        JOIN fuentes f ON n.fuente_id = f.id
        ORDER BY fecha DESC
        LIMIT 200;
    """, fetch=True) or []

    alertas = []

    for r in rows:
        text = f"{r.get('titulo','')} {r.get('descripcion','')}".lower()
        count = sum(1 for p in palabras_riesgo if p in text)

        if count == 0:
            continue

        nivel = "alto" if count >= 4 else "medio" if count >= 2 else "bajo"

        alertas.append({
            "id": r["id"],
            "titulo": r["titulo"],
            "categoria": r["categoria"],
            "fuente": r["fuente"],
            "fecha": r["fecha"].strftime("%Y-%m-%d %H:%M") if r.get("fecha") else "",
            "nivel": nivel,
            "conteo": count
        })

    level_sort = {"alto": 0, "medio": 1, "bajo": 2}
    alertas.sort(key=lambda x: (level_sort[x["nivel"]], -x["conteo"]))

    return jsonify(alertas[:30])


# ============================================================
# 🔹 10. NOTICIAS POR DÍA (ÚLTIMOS 30 DÍAS)
# ============================================================

@api_bp.get("/stats/noticias_dia")
def api_stats_noticias_dia():
    """
    Devuelve la cantidad de noticias publicadas por día
    en los últimos 30 días (según fecha_publicacion o fecha_registro).
    """
    sql = """
        SELECT 
            DATE(COALESCE(fecha_publicacion, fecha_registro)) AS fecha,
            COUNT(*) AS total
        FROM noticias
        WHERE COALESCE(fecha_publicacion, fecha_registro) >= CURDATE() - INTERVAL 30 DAY
        GROUP BY DATE(COALESCE(fecha_publicacion, fecha_registro))
        ORDER BY fecha ASC;
    """
    rows = execute_query(sql, fetch=True) or []

    data = [
        {
            "fecha": r["fecha"].strftime("%Y-%m-%d") if r.get("fecha") else "",
            "total": int(r["total"])
        }
        for r in rows
    ]

    return jsonify(data)


# ============================================================
# 🔹 11. NOTIFICACIONES: NUEVA NOTICIA (ADMIN)
# ============================================================

@api_bp.post("/notificaciones/noticia-nueva")
def api_notificar_noticia_nueva():
    """
    Endpoint para notificar cuando se publica una noticia nueva.
    Requiere autenticación de admin.
    
    Body:
    {
        "titulo": "Nueva noticia",
        "categoria": "Política",
        "fuente": "Facebook",
        "id": 123
    }
    """
    
    if session.get("rol") != "admin":
        return jsonify({"error": "No autorizado"}), 403

    data = request.get_json()

    titulo = data.get("titulo", "Nueva noticia")
    categoria = data.get("categoria", "General")
    fuente = data.get("fuente", "Portal")
    noticia_id = data.get("id")

    notif_data = {
        'id': noticia_id,
        'titulo': titulo,
        'categoria': categoria,
        'fuente': fuente
    }

    # Llamar función desde app
    if hasattr(current_app, 'notificar_noticia_nueva'):
        success = current_app.notificar_noticia_nueva(notif_data)
    else:
        success = False

    return jsonify({
        "success": success,
        "mensaje": "Notificación enviada" if success else "WebSocket no disponible"
    })


# ============================================================
# 🔹 12. NOTIFICACIONES: ALERTA DE RIESGO (ADMIN)
# ============================================================

@api_bp.post("/notificaciones/alerta-riesgo")
def api_notificar_alerta_riesgo():
    """
    Endpoint para enviar alertas de riesgo/seguridad.
    
    Body:
    {
        "titulo": "Contenido peligroso",
        "nivel": "alto",
        "descripcion": "Se detectó noticia con contenido peligroso"
    }
    """

    if session.get("rol") != "admin":
        return jsonify({"error": "No autorizado"}), 403

    data = request.get_json()

    titulo = data.get("titulo", "Alerta de Seguridad")
    nivel = data.get("nivel", "medio")
    descripcion = data.get("descripcion", "")

    alerta_data = {
        'titulo': titulo,
        'nivel': nivel,
        'descripcion': descripcion
    }

    # Llamar función desde app
    if hasattr(current_app, 'notificar_alerta_riesgo'):
        success = current_app.notificar_alerta_riesgo(alerta_data)
    else:
        success = False

    return jsonify({
        "success": success,
        "mensaje": "Alerta enviada" if success else "WebSocket no disponible"
    })


# ============================================================
# 🔹 13. NOTIFICACIONES: PERSONALIZADA (ADMIN)
# ============================================================

@api_bp.post("/notificaciones/personalizada")
def api_notificacion_personalizada():
    """
    Endpoint para enviar notificaciones personalizadas.
    
    Body:
    {
        "titulo": "Mensaje personalizado",
        "tipo": "success",
        "categoria": "General"
    }
    """

    if session.get("rol") != "admin":
        return jsonify({"error": "No autorizado"}), 403

    data = request.get_json()

    titulo = data.get("titulo", "Notificación")
    tipo = data.get("tipo", "info")
    categoria = data.get("categoria", "General")

    # Llamar función desde app
    if hasattr(current_app, 'enviar_notificacion_personalizada'):
        success = current_app.enviar_notificacion_personalizada(titulo, tipo, categoria)
    else:
        success = False

    return jsonify({
        "success": success,
        "mensaje": "Notificación enviada" if success else "WebSocket no disponible"
    })


# ============================================================
# 🔹 14. OBTENER ESTADO DE CONEXIONES (ADMIN)
# ============================================================

@api_bp.get("/notificaciones/estado")
def api_estado_notificaciones():
    """
    Retorna el estado de las conexiones WebSocket.
    Solo para admin.
    """

    if session.get("rol") != "admin":
        return jsonify({"error": "No autorizado"}), 403

    clientes = 0
    if hasattr(current_app, 'obtener_clientes_conectados'):
        clientes = current_app.obtener_clientes_conectados()

    return jsonify({
        "clientes_conectados": clientes,
        "servidor": "activo",
        "notificaciones": "habilitadas"
    })