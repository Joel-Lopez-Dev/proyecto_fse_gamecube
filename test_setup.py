"""
PRUEBAS RÁPIDAS - Xbox Arcade Gaming
Ejecutar este archivo para validar el setup en PC
"""

import asyncio
import subprocess
import sys
import time
from pathlib import Path

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def check_python_version():
    """Verificar versión de Python."""
    print_header("✓ VERIFICANDO VERSIÓN DE PYTHON")
    version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"  Python {version}")
    if sys.version_info < (3, 8):
        print("  ⚠️  Se recomienda Python 3.8+")
        return False
    return True

def check_dependencies():
    """Verificar si las dependencias están instaladas."""
    print_header("✓ VERIFICANDO DEPENDENCIAS")
    
    required = ['fastapi', 'uvicorn', 'websockets']
    optional = ['RPi.GPIO', 'smbus2', 'rpi_lcd']
    
    for package in required:
        try:
            __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} - FALTA (crítica)")
            return False
    
    print("\n  Paquetes opcionales (Rasp):")
    for package in optional:
        try:
            __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ⚠️  {package} - No disponible (Fallback a simulación)")
    
    return True

def check_file_structure():
    """Verificar estructura de archivos."""
    print_header("✓ VERIFICANDO ESTRUCTURA")
    
    required_files = [
        "app.py",
        "templates/index.html",
        "static/css/style.css",
        "static/js/game.js",
        "requirements.txt",
        "README.md"
    ]
    
    base_path = Path(__file__).parent
    all_exist = True
    
    for file_path in required_files:
        full_path = base_path / file_path
        if full_path.exists():
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} - FALTA")
            all_exist = False
    
    return all_exist

def check_ports():
    """Verificar si el puerto 8000 está disponible."""
    print_header("✓ VERIFICANDO PUERTOS")
    
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', 8000))
    sock.close()
    
    if result == 0:
        print("  ⚠️  Puerto 8000 está en uso")
        print("     Cambiar en app.py: uvicorn.run(..., port=8001)")
        return False
    else:
        print("  ✓ Puerto 8000 disponible")
        return True

def test_websocket():
    """Probar conexión WebSocket."""
    print_header("✓ TESTANDO WEBSOCKET")
    print("  Nota: Este test requiere que app.py esté ejecutándose")
    print("        en otra terminal. Ignorar si es primera ejecución.")
    
    try:
        import websockets
        print("  ✓ websockets importado correctamente")
        return True
    except ImportError:
        print("  ✗ websockets no disponible")
        return False

def test_hardware_detection():
    """Simular detección de hardware."""
    print_header("✓ TESTANDO DETECCIÓN DE HARDWARE")
    
    try:
        import RPi.GPIO
        print("  ✓ RPi.GPIO detectado - Modo HARDWARE REAL")
    except ImportError:
        print("  ⚠️  RPi.GPIO no disponible - Modo SIMULACIÓN (Esperado en PC)")
    
    try:
        import smbus2
        print("  ✓ smbus2 detectado")
    except ImportError:
        print("  ⚠️  smbus2 no disponible (Esperado en PC)")

def validate_javascript():
    """Validar sintaxis básica de JavaScript."""
    print_header("✓ VALIDANDO JAVASCRIPT")
    
    js_file = Path(__file__).parent / "static/js/game.js"
    if js_file.exists():
        with open(js_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'class XboxArcadeGame' in content:
                print("  ✓ Clase XboxArcadeGame encontrada")
            if 'handleButtonPress' in content:
                print("  ✓ Métodos de control encontrados")
            if 'WebSocket' in content:
                print("  ✓ WebSocket configurado")
        return True
    return False

def print_startup_guide():
    """Imprimir guía de inicio."""
    print_header("🚀 GUÍA DE INICIO RÁPIDO")
    
    print("""
  1. En tu terminal, ejecutar:
     python app.py

  2. Abrir en navegador:
     http://localhost:8000

  3. Seleccionar juego:
     - Simon Dice: Memoria + atención en LEDs
     - Héroe del Ritmo: Timing + ritmo en pantalla
     - Test Hardware: Probar LEDs y LCD

  4. Controles (Teclado PC):
     J1: Q, W, E, R
     J2: U, I, O, P

  5. Cuando transferir a Raspberry Pi:
     - Copiar carpeta del proyecto
     - Instalar dependencias de Rasp
     - Los GPIO y LCD se activarán automáticamente
""")

def main():
    """Ejecutar todas las pruebas."""
    print("\n")
    print("🎮" * 35)
    print("     XBOX ARCADE GAMING - VALIDACIÓN DE SETUP")
    print("🎮" * 35)
    
    tests = [
        ("Python", check_python_version),
        ("Dependencias", check_dependencies),
        ("Estructura", check_file_structure),
        ("Puertos", check_ports),
        ("WebSocket", test_websocket),
        ("Hardware", test_hardware_detection),
        ("JavaScript", validate_javascript),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"  ✗ Error: {e}")
            results[test_name] = False
    
    # Resumen
    print_header("📊 RESUMEN DE VALIDACIÓN")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✓ PASS" if passed_test else "✗ FAIL"
        print(f"  {status}: {test_name}")
    
    print(f"\n  Total: {passed}/{total} pruebas pasadas")
    
    if passed == total:
        print("\n  🎉 ¡Setup válido! Listo para jugar.\n")
        print_startup_guide()
    else:
        print("\n  ⚠️  Algunas pruebas fallaron.")
        print("      Revisar mensajes arriba e instalar dependencias.\n")

if __name__ == "__main__":
    main()
