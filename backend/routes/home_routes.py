# backend/routes/home_routes.py

from flask import Blueprint, render_template, request
from db import execute_query
from datetime import datetime

home_bp = Blueprint("home", __name__)

# ----------------------------------------------------
# 📌 Funciones internas del controlador
# ----------------------------------------------------
def obtener_fuentes():
    sql = "SELECT id, nombre FROM fuentes ORDER BY nombre;"
    return execute_query(sql, fetch=True) or []

def obtener_categorias():
    sql = """
        SELECT DISTINCT categoria
        FROM noticias
        WHERE categoria IS NOT NULL AND categoria <> ''
        ORDER BY categoria;
    """
    data = execute_query(sql, fetch=True) or []
    return [d["categoria"] for d in data]

def obtener_publicaciones_fb(limit=6):
    sql = """
        SELECT n.titulo, n.descripcion, n.url_imagen, n.url_noticia AS url,
               n.fecha_publicacion
        FROM noticias n
        JOIN fuentes f ON n.fuente_id = f.id
        WHERE f.nombre = 'Facebook'
        ORDER BY COALESCE(n.fecha_publicacion, n.fecha_registro) DESC
        LIMIT %s;
    """
    return execute_query(sql, (limit,), fetch=True) or []

def obtener_estadisticas():
    sql = """
        SELECT COUNT(*) AS total_noticias,
               COUNT(DISTINCT fuente_id) AS total_fuentes,
               COUNT(DISTINCT categoria) AS total_categorias
        FROM noticias;
    """
    res = execute_query(sql, fetch=True)
    return res[0] if res else {}

def obtener_noticias(categoria="", page=1, per_page=12):
    offset = (page - 1) * per_page

    sql = """
        SELECT 
            n.titulo, n.descripcion, n.url_imagen, n.url_noticia,
            n.fecha_publicacion, n.categoria,
            f.nombre AS fuente
        FROM noticias n
        JOIN fuentes f ON n.fuente_id = f.id
        WHERE (%s = '' OR n.categoria = %s)
        ORDER BY COALESCE(n.fecha_publicacion, n.fecha_registro) DESC
        LIMIT %s OFFSET %s;
    """
    params = (categoria, categoria, per_page, offset)
    data = execute_query(sql, params, fetch=True) or []

    sql_count = """
        SELECT COUNT(*) AS total
        FROM noticias
        WHERE (%s = '' OR categoria = %s)
    """
    total = execute_query(sql_count, (categoria, categoria), fetch=True)[0]["total"]
    total_pages = (total // per_page) + (1 if total % per_page else 0)

    return data, total, total_pages


# ----------------------------------------------------
# 🏠 RUTA HOME FINAL PROFESIONAL
# ----------------------------------------------------
@home_bp.route("/")
def home():
    categoria = request.args.get("categoria", "").strip()
    page = int(request.args.get("page", 1))

    noticias, total, total_paginas = obtener_noticias(
        categoria=categoria,
        page=page
    )

    return render_template(
        "index.html",
        fuentes=obtener_fuentes(),
        categorias=obtener_categorias(),
        noticias=noticias,
        publicaciones_fb=obtener_publicaciones_fb(),
        stats=obtener_estadisticas(),
        total_noticias_filtradas=total,
        total_paginas=total_paginas
    )
