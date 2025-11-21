# ============================================================
# 🔔 websocket_service.py — WebSocket Notificaciones (PRO 2025)
# ============================================================

from flask_socketio import SocketIO, emit, join_room, leave_room
from datetime import datetime
import json

socketio = None
clientes_conectados = []

# ============================================================
# INICIALIZAR SOCKETIO
# ============================================================
def inicializar_socketio(app):
    global socketio
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    @socketio.on('connect')
    def handle_connect():
        cliente_id = request.sid
        clientes_conectados.append(cliente_id)
        print(f"✅ Cliente conectado: {cliente_id}")
        print(f"📊 Clientes activos: {len(clientes_conectados)}")
        emit('conexion_exitosa', {'mensaje': 'Conectado al servidor'})

    @socketio.on('disconnect')
    def handle_disconnect():
        cliente_id = request.sid
        if cliente_id in clientes_conectados:
            clientes_conectados.remove(cliente_id)
        print(f"❌ Cliente desconectado: {cliente_id}")
        print(f"📊 Clientes activos: {len(clientes_conectados)}")

    @socketio.on('mensaje')
    def handle_mensaje(data):
        print(f"📨 Mensaje recibido: {data}")
        emit('respuesta', {'status': 'recibido'}, broadcast=True)

    return socketio


# ============================================================
# ENVIAR NOTIFICACIÓN DE NOTICIA NUEVA
# ============================================================
def notificar_noticia_nueva(noticia_data):
    """
    Envía notificación a todos los clientes cuando hay una noticia nueva.
    
    Args:
        noticia_data: dict con {
            'id': int,
            'titulo': str,
            'categoria': str,
            'fuente': str,
            'url_noticia': str
        }
    """
    if socketio is None:
        return False

    payload = {
        'type': 'noticia_nueva',
        'titulo': noticia_data.get('titulo', 'Nueva noticia'),
        'categoria': noticia_data.get('categoria', 'General'),
        'fuente': noticia_data.get('fuente', 'Portal'),
        'timestamp': datetime.now().isoformat(),
        'id': noticia_data.get('id')
    }

    print(f"🔔 Notificando noticia nueva: {payload['titulo']}")
    socketio.emit('noticia_nueva', payload, broadcast=True)
    return True


# ============================================================
# NOTIFICACIÓN DE ALERTA DE RIESGO
# ============================================================
def notificar_alerta_riesgo(alerta_data):
    """
    Envía notificación de alerta/riesgo detectado.
    
    Args:
        alerta_data: dict con {
            'titulo': str,
            'nivel': str (bajo/medio/alto),
            'descripcion': str
        }
    """
    if socketio is None:
        return False

    payload = {
        'type': 'alerta_riesgo',
        'titulo': alerta_data.get('titulo', 'Alerta'),
        'nivel': alerta_data.get('nivel', 'medio'),
        'descripcion': alerta_data.get('descripcion', ''),
        'timestamp': datetime.now().isoformat()
    }

    print(f"⚠️ Alerta enviada: [{payload['nivel'].upper()}] {payload['titulo']}")
    socketio.emit('alerta', payload, broadcast=True)
    return True


# ============================================================
# NOTIFICACIÓN PERSONALIZADA
# ============================================================
def enviar_notificacion_personalizada(titulo, tipo='info', categoria='General'):
    """
    Envía una notificación personalizada a todos los clientes.
    
    Args:
        titulo: str - Mensaje de la notificación
        tipo: str - 'success', 'warning', 'danger', 'info'
        categoria: str - Categoría de la notificación
    """
    if socketio is None:
        return False

    payload = {
        'type': 'notificacion',
        'titulo': titulo,
        'tipo': tipo,
        'categoria': categoria,
        'timestamp': datetime.now().isoformat()
    }

    print(f"📢 Notificación: {titulo}")
    socketio.emit('notificacion', payload, broadcast=True)
    return True


# ============================================================
# OBTENER CLIENTES CONECTADOS
# ============================================================
def obtener_clientes_conectados():
    """Retorna la cantidad de clientes conectados."""
    return len(clientes_conectados)


# ============================================================
# ENVIAR ESTADÍSTICAS EN VIVO
# ============================================================
def enviar_estadisticas_vivas(stats):
    """
    Envía estadísticas actualizadas en tiempo real.
    """
    if socketio is None:
        return False

    payload = {
        'type': 'estadisticas_vivas',
        'stats': stats,
        'timestamp': datetime.now().isoformat()
    }

    socketio.emit('estadisticas', payload, broadcast=True)
    return True