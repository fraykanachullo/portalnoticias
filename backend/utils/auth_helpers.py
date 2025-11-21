from functools import wraps
from flask import session, redirect, url_for, flash


def login_required(rol=None):
    """
    Decorador para proteger rutas.
    - Si rol es None: solo requiere estar logueado.
    - Si rol = 'admin': usuario debe tener rol admin.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user_id = session.get("user_id")
            user_rol = session.get("user_rol")

            if not user_id:
                flash("Debes iniciar sesión para acceder a esta sección.", "warning")
                return redirect(url_for("auth.login"))

            if rol and user_rol != rol:
                flash("No tienes permisos para acceder aquí.", "danger")
                return redirect(url_for("index"))

            return fn(*args, **kwargs)
        return wrapper
    return decorator
