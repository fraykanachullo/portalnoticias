# ============================================================
# 🧠 auth_service.py — Lógica de Autenticación (PRO)
# ============================================================

from db import execute_query
from werkzeug.security import generate_password_hash, check_password_hash


# ------------------------------------------------------------
# Obtener usuario por correo
# ------------------------------------------------------------
def obtener_usuario_por_email(email):
    sql = "SELECT * FROM usuarios WHERE email = %s LIMIT 1"
    res = execute_query(sql, (email,), fetch=True)
    return res[0] if res else None


# ------------------------------------------------------------
# Crear nuevo usuario
# ------------------------------------------------------------
def crear_usuario(nombre, email, password, rol="usuario"):
    # Verificar si ya existe
    if obtener_usuario_por_email(email):
        return True, "Ya existe"

    password_hash = generate_password_hash(password)

    sql = """
        INSERT INTO usuarios (nombre, email, password_hash, rol)
        VALUES (%s, %s, %s, %s)
    """
    execute_query(sql, (nombre, email, password_hash, rol), commit=True)
    return True, "Usuario creado"


# ------------------------------------------------------------
# Verificar login del usuario
# ------------------------------------------------------------
def verificar_credenciales(email, password):
    user = obtener_usuario_por_email(email)
    if not user:
        return None
    
    # prevenir crash por hash vacío
    if not user["password_hash"]:
        return None
    
    try:
        if check_password_hash(user["password_hash"], password):
            return user
    except Exception as e:
        print("ERROR HASH:", e)
        return None

    return None
