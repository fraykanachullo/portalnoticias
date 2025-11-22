from flask import Blueprint, render_template, redirect, session
from backend.services.dashboard_service import (
    obtener_estadisticas_generales,
    obtener_ultimas_noticias,
    obtener_sentimiento_general,
)

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/auth/login")

    stats = obtener_estadisticas_generales()
    ultimas_noticias = obtener_ultimas_noticias(10)
    sentimiento = obtener_sentimiento_general()

    return render_template(
        "user/dashboard.html",
        stats=stats,
        ultimas_noticias=ultimas_noticias,
        sentimiento=sentimiento
    )
