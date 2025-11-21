from flask import (
    Blueprint, render_template, session, redirect,
    request, flash, url_for
)
from db import execute_query
from datetime import datetime
import os

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# =========================================
# 🔐 PROTEGER TODAS LAS RUTAS ADMIN
# =========================================
@admin_bp.before_request
def proteger_admin():
    if "user_id" not in session or session.get("rol") != "admin":
        return redirect("/auth/login")


# =========================================
# 🧊 DASHBOARD ADMIN (RESUMEN GENERAL)
# =========================================
@admin_bp.route("/")
def admin_dashboard():
    # Totales generales
    stats = execute_query("""
        SELECT
            (SELECT COUNT(*) FROM noticias)  AS total_noticias,
            (SELECT COUNT(*) FROM fuentes)   AS total_fuentes,
            (SELECT COUNT(*) FROM usuarios)  AS total_usuarios
    """, fetch=True)
    stats = stats[0] if stats else {
        "total_noticias": 0,
        "total_fuentes": 0,
        "total_usuarios": 0
    }

    # Logs de hoy
    LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "logs"))
    today_file = f"app_{datetime.now().strftime('%Y-%m-%d')}.log"
    log_path = os.path.join(LOG_DIR, today_file)

    if os.path.exists(log_path):
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                logs = f.read()[-8000:]   # últimos 8000 chars
        except Exception:
            logs = "⚠️ No se pudieron leer los logs."
    else:
        logs = f"⚠️ No existe el archivo: {today_file}"

    return render_template(
        "admin/admin_dashboard.html",
        stats=stats,
        logs=logs,
    )


# =========================================
# 📄 LOGS EN PANTALLA COMPLETA
# =========================================
@admin_bp.route("/logs")
def admin_logs():
    LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "logs"))
    today_file = f"app_{datetime.now().strftime('%Y-%m-%d')}.log"
    log_path = os.path.join(LOG_DIR, today_file)

    if os.path.exists(log_path):
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                logs = f.read()[-15000:]
        except Exception:
            logs = "⚠️ No se pudieron leer los logs."
    else:
        logs = f"⚠️ No existe el archivo: {today_file}"

    return render_template("admin/admin_logs.html", logs=logs)


# =========================================
# 👥 LISTADO DE USUARIOS
# =========================================
@admin_bp.route("/usuarios")
def admin_usuarios():
    usuarios = execute_query("""
        SELECT id, nombre, email, rol, fecha_registro
        FROM usuarios
        ORDER BY fecha_registro DESC;
    """, fetch=True) or []

    return render_template("admin/admin_users.html", usuarios=usuarios)


# =========================================
# 📰 LISTADO DE NOTICIAS (A - List)
# =========================================
@admin_bp.route("/noticias")
def admin_noticias():
    q = request.args.get("q", "").strip()
    fuente = request.args.get("fuente", "").strip()
    categoria = request.args.get("categoria", "").strip()

    filtros = []
    params = []

    if q:
        filtros.append("n.titulo LIKE %s")
        params.append(f"%{q}%")

    if fuente:
        filtros.append("f.id = %s")
        params.append(fuente)

    if categoria:
        filtros.append("n.categoria = %s")
        params.append(categoria)

    where = ""
    if filtros:
        where = "WHERE " + " AND ".join(filtros)

    sql = f"""
        SELECT
            n.id, n.titulo, n.categoria,
            COALESCE(n.fecha_publicacion, n.fecha_registro) AS fecha,
            f.nombre AS fuente
        FROM noticias n
        JOIN fuentes f ON n.fuente_id = f.id
        {where}
        ORDER BY fecha DESC
        LIMIT 100;
    """

    noticias = execute_query(sql, tuple(params), fetch=True) or []

    fuentes = execute_query(
        "SELECT id, nombre FROM fuentes ORDER BY nombre;",
        fetch=True
    ) or []

    categorias_rows = execute_query("""
        SELECT DISTINCT categoria
        FROM noticias
        WHERE categoria IS NOT NULL AND categoria <> ''
        ORDER BY categoria;
    """, fetch=True) or []

    categorias = [c["categoria"] for c in categorias_rows]

    return render_template(
        "admin/admin_noticias.html",
        noticias=noticias,
        fuentes=fuentes,
        categorias=categorias,
        q=q,
        fuente_sel=fuente,
        categoria_sel=categoria
    )


# =========================================
# 📰 CREAR NOTICIA (A - Create)
# =========================================
@admin_bp.route("/noticia/nueva", methods=["GET", "POST"])
def admin_noticia_nueva():
    fuentes = execute_query(
        "SELECT id, nombre FROM fuentes ORDER BY nombre;",
        fetch=True
    ) or []

    if request.method == "POST":
        fuente_id = request.form.get("fuente_id")
        titulo = request.form.get("titulo", "").strip()
        categoria = request.form.get("categoria", "").strip() or "General"
        subtitulo = request.form.get("subtitulo", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        url_noticia = request.form.get("url_noticia", "").strip()
        url_imagen = request.form.get("url_imagen", "").strip()
        fecha_publicacion = request.form.get("fecha_publicacion", "").strip()

        if not titulo or not url_noticia or not fuente_id:
            flash("Título, URL y Fuente son obligatorios.", "danger")
            return render_template(
                "admin/admin_noticia_form.html",
                fuentes=fuentes,
                noticia=None
            )

        fecha_value = None
        if fecha_publicacion:
            try:
                fecha_value = datetime.strptime(fecha_publicacion, "%Y-%m-%d")
            except ValueError:
                flash("Formato de fecha inválido.", "warning")

        sql = """
            INSERT INTO noticias (
                fuente_id, titulo, categoria, subtitulo, descripcion,
                url_noticia, url_imagen, fecha_publicacion, fecha_registro
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,NOW());
        """

        execute_query(
            sql,
            (
                int(fuente_id), titulo[:255], categoria, subtitulo,
                descripcion, url_noticia, url_imagen, fecha_value
            ),
            commit=True
        )

        flash("Noticia creada correctamente ✅", "success")
        return redirect(url_for("admin.admin_noticias"))

    return render_template(
        "admin/admin_noticia_form.html",
        fuentes=fuentes,
        noticia=None
    )


# =========================================
# 📰 EDITAR NOTICIA (A - Update)
# =========================================
@admin_bp.route("/noticia/editar/<int:noticia_id>", methods=["GET", "POST"])
def admin_noticia_editar(noticia_id):
    res = execute_query(
        "SELECT * FROM noticias WHERE id = %s LIMIT 1",
        (noticia_id,), fetch=True
    )

    if not res:
        flash("Noticia no encontrada.", "warning")
        return redirect(url_for("admin.admin_noticias"))

    noticia = res[0]

    fuentes = execute_query(
        "SELECT id, nombre FROM fuentes ORDER BY nombre;",
        fetch=True
    ) or []

    if request.method == "POST":
        fuente_id = request.form.get("fuente_id")
        titulo = request.form.get("titulo", "").strip()
        categoria = request.form.get("categoria", "").strip() or "General"
        subtitulo = request.form.get("subtitulo", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        url_noticia = request.form.get("url_noticia", "").strip()
        url_imagen = request.form.get("url_imagen", "").strip()
        fecha_publicacion = request.form.get("fecha_publicacion", "").strip()

        if not titulo or not url_noticia or not fuente_id:
            flash("Faltan datos obligatorios.", "danger")
            return render_template(
                "admin/admin_noticia_form.html",
                fuentes=fuentes,
                noticia=noticia
            )

        fecha_value = None
        if fecha_publicacion:
            try:
                fecha_value = datetime.strptime(fecha_publicacion, "%Y-%m-%d")
            except ValueError:
                flash("Formato de fecha inválido.", "warning")

        sql = """
            UPDATE noticias SET
                fuente_id=%s, titulo=%s, categoria=%s,
                subtitulo=%s, descripcion=%s,
                url_noticia=%s, url_imagen=%s,
                fecha_publicacion=%s
            WHERE id=%s;
        """

        execute_query(
            sql,
            (
                int(fuente_id), titulo[:255], categoria, subtitulo,
                descripcion, url_noticia, url_imagen,
                fecha_value, noticia_id
            ),
            commit=True
        )

        flash("Noticia actualizada correctamente ✅", "success")
        return redirect(url_for("admin.admin_noticias"))

    if noticia.get("fecha_publicacion"):
        noticia["fecha_publicacion_str"] = noticia["fecha_publicacion"].strftime("%Y-%m-%d")
    else:
        noticia["fecha_publicacion_str"] = ""

    return render_template(
        "admin/admin_noticia_form.html",
        fuentes=fuentes,
        noticia=noticia
    )


# =========================================
# 📰 ELIMINAR NOTICIA (A - Delete)
# =========================================
@admin_bp.route("/noticia/eliminar/<int:noticia_id>", methods=["POST"])
def admin_noticia_eliminar(noticia_id):
    execute_query(
        "DELETE FROM noticias WHERE id = %s",
        (noticia_id,), commit=True
    )
    flash("Noticia eliminada correctamente 🗑️", "info")
    return redirect(url_for("admin.admin_noticias"))
