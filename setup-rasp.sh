#!/bin/bash
# Setup Raspberry Pi - Instalación completa
# Ejecutar con: sudo bash setup-rasp.sh

set -e

echo "======================================================================"
echo "GameCube - Proyecto Final FSE - SETUP RASPBERRY PI"
echo "======================================================================"
echo ""

# Verificar privilegios
if [[ $EUID -ne 0 ]]; then
    echo "❌ Este script debe ejecutarse con sudo"
    exit 1
fi

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 1. Actualizar sistema
echo "1/6 Actualizando sistema..."
apt-get update -qq
apt-get upgrade -y -qq
echo "✓ Sistema actualizado"

# 2. Instalar dependencias del sistema
echo "2/6 Instalando dependencias del sistema..."
apt-get install -y -qq \
    python3-pip \
    python3-venv \
    git \
    i2c-tools \
    omxplayer \
    chromium-browser \
    xdotool
echo "✓ Dependencias instaladas"

# 3. Habilitar I2C
echo "3/6 Habilitando I2C para LCD..."
if ! grep -q "i2c-dev" /etc/modules; then
    echo "i2c-dev" >> /etc/modules
fi
if ! grep -q "i2c-bcm2708" /etc/modules; then
    echo "i2c-bcm2708" >> /etc/modules
fi
raspi-config nonint do_i2c 0
echo "✓ I2C habilitado"

# 4. Crear entorno virtual e instalar Python packages
echo "4/6 Configurando entorno Python..."
cd "$PROJECT_DIR"

# Si el venv ya existe, eliminarlo
if [ -d "env" ]; then
    rm -rf env
fi

python3 -m venv env
source env/bin/activate
pip install --upgrade pip setuptools wheel -q

# Instalar dependencias
pip install -r requirements.txt -q

# Instalar librerías GPIO (solo en Rasp)
echo "   Instalando librerías GPIO..."
pip install RPi.GPIO smbus2 rpi-lcd -q

echo "✓ Entorno Python configurado"

# 5. Crear directorio videos
echo "5/6 Preparando directorios..."
mkdir -p videos
echo "✓ Carpeta videos creada"

# 6. Configurar autostart
echo "6/6 Configurando autostart..."
bash "$PROJECT_DIR/gamecube-autostart.sh"
echo "✓ Autostart configurado"

echo ""
echo "======================================================================"
echo "✓ INSTALACIÓN COMPLETADA"
echo "======================================================================"
echo ""
echo "Próximos pasos:"
echo ""
echo "1. COLOCA EL VIDEO (opcional):"
echo "   cp /ruta/a/gamecube.mp4 $PROJECT_DIR/videos/"
echo ""
echo "2. VERIFICA LAS CONEXIONES:"
echo "   - Consulta: cat $PROJECT_DIR/CONEXIONES.txt"
echo "   - 8 botones GPIO"
echo "   - 4 LEDs GPIO"
echo "   - LCD I2C (0x27)"
echo ""
echo "3. INICIA MANUALMENTE (prueba):"
echo "   sudo systemctl start gamecube"
echo "   Luego abre: http://$(hostname -I | awk '{print $1}'):8000"
echo ""
echo "4. O REINICIA PARA AUTOSTART:"
echo "   sudo reboot"
echo ""
echo "======================================================================"
echo ""
