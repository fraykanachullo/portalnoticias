# ============================================================
# 🔐 auth_routes.py — Autenticación (Login, Registro, Logout)
# ============================================================

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from backend.services.auth_service import crear_usuario, verificar_credenciales

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


# ------------------------------------------------------------
# 🟢 LOGIN
# ------------------------------------------------------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        user = verificar_credenciales(email, password)

        if user:
            # Crear sesión segura
            session["user_id"] = user["id"]
            session["nombre"] = user["nombre"]
            session["rol"] = user["rol"]

            flash(f"Bienvenido, {user['nombre']}", "success")

            # Redirigir según rol
            if user["rol"] == "admin":
                return redirect("/admin")
            else:
                return redirect("/dashboard")

        flash("Correo o contraseña incorrectos", "danger")

    return render_template("login.html")


# ------------------------------------------------------------
# 🔵 REGISTRO DE USUARIOS
# ------------------------------------------------------------
@auth_bp.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        ok, msg = crear_usuario(nombre, email, password, rol="usuario")

        if ok:
            flash("Cuenta creada correctamente. Ahora puedes iniciar sesión.", "success")
            return redirect(url_for("auth.login"))
        else:
            flash(msg, "danger")

    return render_template("registro.html")


# ------------------------------------------------------------
# 🔴 LOGOUT
# ------------------------------------------------------------
@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada correctamente.", "info")
    return redirect("/")
