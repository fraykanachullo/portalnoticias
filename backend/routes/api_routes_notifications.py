# ============================================================
# 📢 Rutas API para Notificaciones (Agregar a api_routes.py)
# ============================================================

# AGREGAR AL INICIO DEL ARCHIVO:
from backend.services.websocket_service import (
    notificar_noticia_nueva,
    notificar_alerta_riesgo,
    enviar_notificacion_personalizada,
    obtener_clientes_conectados
)


# ============================================================
# 🔹 NOTIFICACIÓN: NUEVA NOTICIA
# ============================================================
@api_bp.post("/notificaciones/noticia-nueva")
def api_notificar_noticia_nueva():
    """
    Endpoint para notificar cuando se publica una noticia nueva.
    Requiere autenticación de admin.
    """
    
    # Verificar que sea admin
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

    success = notificar_noticia_nueva(notif_data)

    return jsonify({
        "success": success,
        "mensaje": "Notificación enviada" if success else "Error al enviar"
    })


# ============================================================
# 🔹 NOTIFICACIÓN: ALERTA DE RIESGO
# ============================================================
@api_bp.post("/notificaciones/alerta-riesgo")
def api_notificar_alerta_riesgo():
    """
    Endpoint para enviar alertas de riesgo/seguridad.
    """

    if session.get("rol") != "admin":
        return jsonify({"error": "No autorizado"}), 403

    data = request.get_json()

    titulo = data.get("titulo", "Alerta de Seguridad")
    nivel = data.get("nivel", "medio")  # bajo, medio, alto
    descripcion = data.get("descripcion", "")

    alerta_data = {
        'titulo': titulo,
        'nivel': nivel,
        'descripcion': descripcion
    }

    success = notificar_alerta_riesgo(alerta_data)

    return jsonify({
        "success": success,
        "mensaje": "Alerta enviada" if success else "Error al enviar"
    })


# ============================================================
# 🔹 NOTIFICACIÓN: PERSONALIZADA
# ============================================================
@api_bp.post("/notificaciones/personalizada")
def api_notificacion_personalizada():
    """
    Endpoint para enviar notificaciones personalizadas.
    """

    if session.get("rol") != "admin":
        return jsonify({"error": "No autorizado"}), 403

    data = request.get_json()

    titulo = data.get("titulo", "Notificación")
    tipo = data.get("tipo", "info")  # success, warning, danger, info
    categoria = data.get("categoria", "General")

    success = enviar_notificacion_personalizada(titulo, tipo, categoria)

    return jsonify({
        "success": success,
        "mensaje": "Notificación enviada" if success else "Error al enviar"
    })


# ============================================================
# 🔹 OBTENER ESTADO DE CONEXIONES
# ============================================================
@api_bp.get("/notificaciones/estado")
def api_estado_notificaciones():
    """
    Retorna el estado de las conexiones WebSocket.
    Solo para admin.
    """

    if session.get("rol") != "admin":
        return jsonify({"error": "No autorizado"}), 403

    clientes = obtener_clientes_conectados()

    return jsonify({
        "clientes_conectados": clientes,
        "servidor": "activo",
        "notificaciones": "habilitadas"
    })