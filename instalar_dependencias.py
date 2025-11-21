#!/usr/bin/env python3
# ============================================================
# 📦 instalar_dependencias.py — Instalar todos los paquetes
# ============================================================

import subprocess
import sys

print("=" * 70)
print("📦 INSTALADOR DE DEPENDENCIAS - Portal de Noticias")
print("=" * 70)
print()

# Lista de dependencias necesarias
dependencias = [
    ("flask", "Flask", "Framework web"),
    ("flask-session", "Flask-Session", "Manejo de sesiones"),
    ("mysql-connector-python", "MySQL Connector", "Conexión a MySQL"),
    ("requests", "Requests", "Hacer requests HTTP"),
    ("beautifulsoup4", "BeautifulSoup", "Web scraping"),
    ("python-dotenv", "python-dotenv", "Variables de entorno"),
    ("schedule", "Schedule", "Tareas programadas"),
    ("wordcloud", "WordCloud", "Generación de word clouds"),
]

# Dependencias opcionales (para notificaciones en tiempo real)
dependencias_opcionales = [
    ("flask-socketio", "Flask-SocketIO", "Notificaciones en tiempo real"),
    ("python-socketio", "python-socketio", "Soporte WebSocket"),
]

print("🔍 Verificando dependencias instaladas...\n")

def verificar_modulo(modulo_pip, modulo_import=None):
    """Verificar si un módulo está instalado"""
    if modulo_import is None:
        modulo_import = modulo_pip.replace("-", "_")
    
    try:
        __import__(modulo_import)
        return True
    except ImportError:
        return False

# Verificar dependencias principales
print("📌 DEPENDENCIAS PRINCIPALES:")
print("-" * 70)

no_instaladas = []

for modulo_pip, nombre, descripcion in dependencias:
    modulo_import = modulo_pip.replace("-", "_")
    instalado = verificar_modulo(modulo_pip, modulo_import)
    
    status = "✅ Instalado" if instalado else "❌ Falta"
    print(f"{status:<20} | {nombre:<25} | {descripcion}")
    
    if not instalado:
        no_instaladas.append(modulo_pip)

print()
print("📌 DEPENDENCIAS OPCIONALES (WebSocket/Notificaciones):")
print("-" * 70)

no_instaladas_opcional = []

for modulo_pip, nombre, descripcion in dependencias_opcionales:
    modulo_import = modulo_pip.replace("-", "_")
    instalado = verificar_modulo(modulo_pip, modulo_import)
    
    status = "✅ Instalado" if instalado else "⚠️  Falta"
    print(f"{status:<20} | {nombre:<25} | {descripcion}")
    
    if not instalado:
        no_instaladas_opcional.append(modulo_pip)

print()
print("=" * 70)

# Instalar dependencias faltantes
if no_instaladas:
    print()
    print(f"⚙️  INSTALANDO {len(no_instaladas)} DEPENDENCIA(S) FALTANTE(S)...")
    print("-" * 70)
    print()
    
    for modulo in no_instaladas:
        print(f"📥 Instalando {modulo}...")
        resultado = subprocess.run(
            [sys.executable, "-m", "pip", "install", modulo, "--quiet"],
            capture_output=True,
            text=True
        )
        
        if resultado.returncode == 0:
            print(f"   ✅ {modulo} instalado correctamente\n")
        else:
            print(f"   ❌ Error instalando {modulo}")
            print(f"   Error: {resultado.stderr}\n")

# Preguntar por dependencias opcionales
if no_instaladas_opcional:
    print()
    print("=" * 70)
    print("❓ DEPENDENCIAS OPCIONALES")
    print("-" * 70)
    print()
    print("Los siguientes paquetes son OPCIONALES pero recomendados:")
    for modulo_pip, nombre, descripcion in dependencias_opcionales:
        print(f"  • {nombre} ({modulo_pip}) - {descripcion}")
    print()
    
    respuesta = input("¿Deseas instalarlos? (s/n): ").strip().lower()
    
    if respuesta == 's':
        print()
        for modulo in no_instaladas_opcional:
            print(f"📥 Instalando {modulo}...")
            resultado = subprocess.run(
                [sys.executable, "-m", "pip", "install", modulo, "--quiet"],
                capture_output=True,
                text=True
            )
            
            if resultado.returncode == 0:
                print(f"   ✅ {modulo} instalado correctamente\n")
            else:
                print(f"   ⚠️  Error instalando {modulo}")
                print(f"   Error: {resultado.stderr}\n")
    else:
        print()
        print("⚠️  Instalación de opcionales cancelada")
        print("💡 Puedes instalarlos después con: pip install flask-socketio python-socketio")

# Verificación final
print()
print("=" * 70)
print("✅ VERIFICACIÓN FINAL")
print("-" * 70)
print()

todas_principales_ok = all(
    verificar_modulo(modulo_pip) 
    for modulo_pip, _, _ in dependencias
)

if todas_principales_ok:
    print("✅ TODAS LAS DEPENDENCIAS PRINCIPALES ESTÁN INSTALADAS")
    print()
    print("🚀 Ahora puedes ejecutar:")
    print("   python app.py")
else:
    print("⚠️  Algunas dependencias aún faltan")
    print()
    print("Intenta instalar manualmente:")
    for modulo in no_instaladas:
        print(f"   pip install {modulo}")

# Resumen
print()
print("=" * 70)
print("📊 RESUMEN")
print("-" * 70)
print()

principales_instaladas = sum(
    1 for modulo_pip, _, _ in dependencias 
    if verificar_modulo(modulo_pip)
)
opcionales_instaladas = sum(
    1 for modulo_pip, _, _ in dependencias_opcionales 
    if verificar_modulo(modulo_pip)
)

print(f"✅ Dependencias principales: {principales_instaladas}/{len(dependencias)}")
print(f"🔧 Dependencias opcionales: {opcionales_instaladas}/{len(dependencias_opcionales)}")
print()

if principales_instaladas == len(dependencias):
    if opcionales_instaladas > 0:
        print("🎉 LISTO: WebSocket ACTIVADO (notificaciones en tiempo real)")
    else:
        print("✨ LISTO: Dashboard funcional (sin notificaciones en tiempo real)")
        print("💡 Tip: Instala flask-socketio para habilitar notificaciones")
else:
    print("⚠️  Algunas dependencias faltan aún")

print()
print("=" * 70)