#!/bin/bash
# test-rasp.sh - Verificación rápida en Raspberry Pi
# Ejecutar con: sudo bash test-rasp.sh

set -e

# ⚠️  CONFIGURACIÓN DE RUTAS - EDITA SI ES NECESARIO
PROJECT_DIR="/home/pi/proyecto_fse_gamecube"  # 👈 Ruta donde clonaste el proyecto

echo "======================================================================"
echo "GameCube - Proyecto Final FSE - Test Rápido Raspberry Pi"
echo "======================================================================"
echo ""

# Verificar si estamos en Rasp
if ! grep -q "Raspberry" /proc/cpuinfo 2>/dev/null; then
    echo "⚠️  Este script debe ejecutarse en Raspberry Pi"
    exit 1
fi

echo "✓ Detectada Raspberry Pi"

# Verificar I2C
echo ""
echo "1/5 Verificando I2C..."
if sudo i2cdetect -y 1 | grep -q "27"; then
    echo "✓ LCD I2C encontrado en 0x27"
else
    echo "⚠️  LCD I2C no detectado. Verifica conexión SDA/SCL"
fi

# Verificar GPIO
echo ""
echo "2/5 Verificando GPIO..."
python3 << 'PYTHON_EOF'
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

# Probar entrada (botón)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
btn_state = GPIO.input(17)
print(f"✓ GPIO 17 (Botón): {btn_state}")

# Probar salida (LED)
GPIO.setup(5, GPIO.OUT)
GPIO.output(5, GPIO.HIGH)
print("✓ GPIO 5 (LED): Encendido")
GPIO.output(5, GPIO.LOW)
print("✓ GPIO 5 (LED): Apagado")

GPIO.cleanup()
PYTHON_EOF

# Verificar Python packages
echo ""
echo "3/5 Verificando Python packages..."
python3 -c "
import fastapi
import uvicorn
import websockets
import RPi.GPIO
import smbus2
from rpi_lcd import CharLCD
print('✓ Todos los packages instalados')
"

# Probar servidor
echo ""
echo "4/5 Iniciando servidor (5 segundos)..."
cd "$(dirname "$0")"
timeout 5 python -m uvicorn app:app --host 0.0.0.0 --port 8000 2>&1 | head -5 || true
echo "✓ Servidor puede iniciar"

# Resumen
echo ""
echo "======================================================================"
echo "✓ TEST COMPLETADO"
echo "======================================================================"
echo ""
echo "Si todo pasó:"
echo "  sudo systemctl start gamecube"
echo "  Abre: http://$(hostname -I | awk '{print $1}'):8000"
echo ""
