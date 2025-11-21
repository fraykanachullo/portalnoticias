# ============================================================
# Rutas IA — Dashboard de Inteligencia de Contenido PRO 2025
# ============================================================

from flask import Blueprint, render_template, session, redirect
from db import execute_query
from backend.services.sentimiento_service import obtener_sentimientos
from backend.services.wordcloud_service import generar_wordcloud
from backend.services.estadisticas_service import top_noticias
import base64

ia_bp = Blueprint("ia", __name__, url_prefix="/admin/ia")


# ============================================================
# 🔐 Protección para admins
# ============================================================

@ia_bp.before_request
def proteger_admin_ia():
    if "user_id" not in session or session.get("rol") != "admin":
        return redirect("/auth/login")


# ============================================================
# 📊 Página principal del Panel IA
# ============================================================

@ia_bp.route("/")
def admin_ia_home():

    # ---------- 1) Sentimiento global ----------
    sent = obtener_sentimientos() or {}
    pos = int(sent.get("pos", 0))
    neg = int(sent.get("neg", 0))
    neu = int(sent.get("neu", 0))

    # ---------- 2) Top 10 noticias ----------
    top10 = top_noticias(10) or []

    # ---------- 3) WordCloud (texto bruto desde BD) ----------
    rows = execute_query("""
        SELECT titulo, descripcion
        FROM noticias
        ORDER BY COALESCE(fecha_publicacion, fecha_registro) DESC
        LIMIT 400;
    """, fetch=True) or []

    texto_bruto = " ".join(
        (r.get("titulo") or "") + " " + (r.get("descripcion") or "")
        for r in rows
    ).strip()

    # ---------- 4) Generar WordCloud HD ----------
    if texto_bruto:
        img_bytes = generar_wordcloud(texto_bruto)
    else:
        img_bytes = generar_wordcloud()

    if img_bytes:
        wordcloud_b64 = base64.b64encode(img_bytes.getvalue()).decode("utf-8")
    else:
        wordcloud_b64 = None

    # ---------- 5) Renderizar ----------
    return render_template(
        "admin/admin_ia.html",
        pos=pos,
        neg=neg,
        neu=neu,
        top10=top10,
        wordcloud_svg=wordcloud_b64,
    )
