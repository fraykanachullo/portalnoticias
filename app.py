# ============================================================
# 🌐 app.py — Portal de Noticias Inteligente (v13.0 PRO)
# Con WebSocket integrado para notificaciones en tiempo real
# ============================================================

from flask import Flask, session
from flask_session import Session
from datetime import datetime
import threading
import logging
import os
import schedule
import time

# Scraper principal
from scraper import main as run_scraper

# ============================================================
# ⚙️ CONFIGURACIÓN DE FLASK
# ============================================================

app = Flask(__name__)
app.secret_key = "super-clave-secreta-2025-mineria"

# Configuración de sesión
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 horas
app.config['SESSION_COOKIE_SECURE'] = False  # Cambiar a True en producción con HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

Session(app)

# ============================================================
# 🔌 CONFIGURACIÓN DE SOCKETIO
# ============================================================

try:
    from flask_socketio import SocketIO, emit, join_room, leave_room
    
    socketio = SocketIO(
        app,
        cors_allowed_origins="*",
        async_mode='threading',
        ping_interval=25,
        ping_timeout=60,
        logger=True,
        engineio_logger=True
    )
    
    SOCKETIO_DISPONIBLE = True
    logging.info("✅ SocketIO inicializado correctamente")
    
except ImportError:
    SOCKETIO_DISPONIBLE = False
    socketio = None
    logging.warning("⚠️ SocketIO no disponible, notificaciones en tiempo real deshabilitadas")
    logging.info("💡 Para habilitar: pip install flask-socketio python-socketio")

# ============================================================
# 📁 CONFIGURACIÓN DE LOGS PROFESIONAL
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "logs")

os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, f"app_{datetime.now().strftime('%Y-%m-%d')}.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logging.info("=" * 60)
logging.info("🔵 Aplicación iniciada correctamente")
logging.info(f"📍 Versión: 13.0 PRO")
logging.info(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
logging.info("=" * 60)

# ============================================================
# 🔐 IMPORTAR BLUEPRINTS
# ============================================================

try:
    from backend.routes.dashboard_routes import dashboard_bp
    from backend.routes.home_routes import home_bp
    from backend.routes.api_routes import api_bp
    from backend.routes.admin_routes import admin_bp
    from backend.routes.auth_routes import auth_bp
    from backend.routes.admin_ia_routes import ia_bp
    from backend.services.auth_service import crear_usuario
    
    # Registrar Blueprints
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(ia_bp)
    
    logging.info("✅ Todos los blueprints registrados correctamente")
    
except ImportError as e:
    logging.error(f"❌ Error importando blueprints: {e}")
    raise

# ============================================================
# 🔌 CONFIGURAR EVENTOS SOCKETIO
# ============================================================

if SOCKETIO_DISPONIBLE:
    
    clientes_conectados = []
    
    @socketio.on('connect')
    def handle_connect():
        """Cuando un cliente se conecta"""
        cliente_id = session.get('user_id', 'anonimo')
        clientes_conectados.append({
            'id': cliente_id,
            'timestamp': datetime.now()
        })
        
        msg = f"✅ Cliente conectado: {cliente_id}"
        logging.info(msg)
        print(msg)
        print(f"📊 Clientes activos: {len(clientes_conectados)}")
        
        emit('conexion_exitosa', {
            'mensaje': 'Conectado al servidor de notificaciones',
            'timestamp': datetime.now().isoformat()
        })
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Cuando un cliente se desconecta"""
        cliente_id = session.get('user_id', 'anonimo')
        clientes_conectados[:] = [c for c in clientes_conectados if c['id'] != cliente_id]
        
        msg = f"❌ Cliente desconectado: {cliente_id}"
        logging.info(msg)
        print(msg)
        print(f"📊 Clientes activos: {len(clientes_conectados)}")
    
    @socketio.on('mensaje')
    def handle_mensaje(data):
        """Recibir mensaje de cliente"""
        print(f"📨 Mensaje recibido: {data}")
        emit('respuesta', {'status': 'recibido'}, broadcast=False)
    
    # ============================================================
    # 🔔 FUNCIONES DE NOTIFICACIONES
    # ============================================================
    
    def notificar_noticia_nueva(noticia_data):
        """
        Envía notificación de noticia nueva a todos los clientes.
        
        Args:
            noticia_data: {
                'id': int,
                'titulo': str,
                'categoria': str,
                'fuente': str,
                'url_noticia': str
            }
        """
        if not SOCKETIO_DISPONIBLE:
            return False
        
        payload = {
            'type': 'noticia_nueva',
            'titulo': noticia_data.get('titulo', 'Nueva noticia'),
            'categoria': noticia_data.get('categoria', 'General'),
            'fuente': noticia_data.get('fuente', 'Portal'),
            'timestamp': datetime.now().isoformat(),
            'id': noticia_data.get('id')
        }
        
        msg = f"🔔 Notificando noticia nueva: {payload['titulo']}"
        logging.info(msg)
        print(msg)
        
        socketio.emit('noticia_nueva', payload, broadcast=True)
        return True
    
    def notificar_alerta_riesgo(alerta_data):
        """
        Envía notificación de alerta/riesgo detectado.
        
        Args:
            alerta_data: {
                'titulo': str,
                'nivel': str (bajo/medio/alto),
                'descripcion': str
            }
        """
        if not SOCKETIO_DISPONIBLE:
            return False
        
        payload = {
            'type': 'alerta_riesgo',
            'titulo': alerta_data.get('titulo', 'Alerta'),
            'nivel': alerta_data.get('nivel', 'medio'),
            'descripcion': alerta_data.get('descripcion', ''),
            'timestamp': datetime.now().isoformat()
        }
        
        msg = f"⚠️ Alerta enviada: [{payload['nivel'].upper()}] {payload['titulo']}"
        logging.info(msg)
        print(msg)
        
        socketio.emit('alerta', payload, broadcast=True)
        return True
    
    def enviar_notificacion_personalizada(titulo, tipo='info', categoria='General'):
        """
        Envía una notificación personalizada a todos los clientes.
        
        Args:
            titulo: str - Mensaje de la notificación
            tipo: str - 'success', 'warning', 'danger', 'info'
            categoria: str - Categoría de la notificación
        """
        if not SOCKETIO_DISPONIBLE:
            return False
        
        payload = {
            'type': 'notificacion',
            'titulo': titulo,
            'tipo': tipo,
            'categoria': categoria,
            'timestamp': datetime.now().isoformat()
        }
        
        msg = f"📢 Notificación: {titulo}"
        logging.info(msg)
        print(msg)
        
        socketio.emit('notificacion', payload, broadcast=True)
        return True
    
    def obtener_clientes_conectados():
        """Retorna la cantidad de clientes conectados."""
        return len(clientes_conectados)
    
    # Exportar funciones para ser usadas en api_routes.py
    app.notificar_noticia_nueva = notificar_noticia_nueva
    app.notificar_alerta_riesgo = notificar_alerta_riesgo
    app.enviar_notificacion_personalizada = enviar_notificacion_personalizada
    app.obtener_clientes_conectados = obtener_clientes_conectados

# ============================================================
# 👤 CREAR USUARIO ADMIN AUTOMÁTICO (SOLO 1 VEZ)
# ============================================================

try:
    crear_usuario("Administrador", "admin@admin.com", "admin123", rol="admin")
    logging.info("🟢 Usuario admin verificado/creado")
except Exception as e:
    logging.error(f"⚠️ Error creando usuario admin: {e}")

# ============================================================
# 🤖 SCRAPER AUTOMÁTICO CADA 10 MINUTOS
# ============================================================

def ejecutar_scraper_periodico():
    """Ejecutar scraper cada 10 minutos en background"""
    schedule.every(10).minutes.do(run_scraper)
    logging.info("⏱️ Scraper programado cada 10 minutos")
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except Exception as e:
            logging.error(f"❌ Error en scraper: {e}")
            time.sleep(60)

# ============================================================
# 🛠️ MANEJO DE ERRORES
# ============================================================

@app.errorhandler(404)
def not_found(error):
    """Página no encontrada"""
    logging.warning(f"404 Error: {error}")
    return {
        "error": "Página no encontrada",
        "status": 404
    }, 404

@app.errorhandler(500)
def server_error(error):
    """Error del servidor"""
    logging.error(f"500 Error: {error}")
    return {
        "error": "Error interno del servidor",
        "status": 500
    }, 500

@app.errorhandler(403)
def forbidden(error):
    """Acceso prohibido"""
    logging.warning(f"403 Error: {error}")
    return {
        "error": "Acceso prohibido",
        "status": 403
    }, 403

# ============================================================
# 📊 RUTAS ÚTILES
# ============================================================

@app.route('/health')
def health_check():
    """Verificar si el servidor está activo"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "socketio": "activado" if SOCKETIO_DISPONIBLE else "desactivado",
        "clientes_conectados": obtener_clientes_conectados() if SOCKETIO_DISPONIBLE else 0
    }

@app.route('/logs/hoy')
def ver_logs_hoy():
    """Ver logs del día actual (solo para debug)"""
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                contenido = f.read()
            return {
                "fecha": datetime.now().strftime('%Y-%m-%d'),
                "archivo": LOG_FILE,
                "contenido": contenido.split('\n')[-100:]  # Últimas 100 líneas
            }
        else:
            return {"error": "No hay logs para hoy"}, 404
    except Exception as e:
        return {"error": str(e)}, 500

# ============================================================
# ⚡ ANTES DE CADA REQUEST
# ============================================================

@app.before_request
def make_session_permanent():
    """Hacer la sesión permanente"""
    session.permanent = True

# ============================================================
# 🚀 MAIN - EJECUTAR APLICACIÓN
# ============================================================

if __name__ == "__main__":
    
    print("=" * 60)
    print("🌍 PORTAL DE NOTICIAS INTELIGENTE v13.0 PRO")
    print("=" * 60)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Iniciar scraper en background
    try:
        scraper_thread = threading.Thread(
            target=ejecutar_scraper_periodico,
            daemon=True,
            name="ScraperThread"
        )
        scraper_thread.start()
        logging.info("🧵 Hilo del scraper iniciado correctamente")
        print("✅ Scraper iniciado en background")
    except Exception as e:
        logging.error(f"❌ Error iniciando scraper: {e}")
        print(f"⚠️ Error iniciando scraper: {e}")
    
    print()
    print("🌐 Accede a: http://127.0.0.1:5000")
    print("📊 Admin: http://127.0.0.1:5000/admin")
    print("📋 Dashboard: http://127.0.0.1:5000/dashboard")
    print()
    
    if SOCKETIO_DISPONIBLE:
        print("✅ WebSocket (notificaciones en tiempo real): ACTIVADO")
        print("🔔 Notificaciones: DISPONIBLES")
    else:
        print("⚠️ WebSocket: DESACTIVADO (instalar flask-socketio para habilitar)")
    
    print()
    print("🔴 Presiona Ctrl+C para detener el servidor")
    print("=" * 60)
    
    logging.info("🚀 Iniciando servidor Flask...")
    
    # Ejecutar con SocketIO si está disponible
    if SOCKETIO_DISPONIBLE:
        socketio.run(
            app,
            host="0.0.0.0",
            port=5000,
            debug=True,
            allow_unsafe_werkzeug=True,
            use_reloader=False
        )
    else:
        # Fallback: ejecutar sin SocketIO
        app.run(
            host="0.0.0.0",
            port=5000,
            debug=True
        )