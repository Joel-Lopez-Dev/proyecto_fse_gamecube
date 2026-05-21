#!/bin/bash
# GameCube - Proyecto Final FSE - Autostart Script
# Configurar servicio systemd para autostart
# Ejecutar con: sudo bash gamecube-autostart.sh

set -e

# ⚠️  CONFIGURACIÓN DE RUTAS - EDITA SI ES NECESARIO
PROJECT_DIR="/home/pi/proyecto_fse_gamecube"          # 👈 Ruta donde clonaste el proyecto
VIDEO_FILE="$PROJECT_DIR/videos/gamecube.mp4"        # 👈 Video intro (poner aquí: cp tu_video.mp4 proyecto/videos/gamecube.mp4)
SYSTEMD_SERVICE="/etc/systemd/system/gamecube.service"
STARTUP_SCRIPT="/usr/local/bin/gamecube-startup.sh"

echo "======================================================================"
echo "GameCube - Proyecto Final FSE - AUTOSTART SETUP"
echo "======================================================================"

# Verificar si estamos en Raspberry Pi
if ! grep -q "Raspberry" /proc/cpuinfo 2>/dev/null; then
    echo "⚠️  Este script está diseñado para Raspberry Pi"
    echo "Continuar? (s/n)"
    read -r response
    if [[ ! "$response" =~ ^[sS]$ ]]; then
        exit 1
    fi
fi

echo "✓ Detectada Raspberry Pi"

# Verificar privilegios
if [[ $EUID -ne 0 ]]; then
    echo "❌ Este script debe ejecutarse con sudo"
    exit 1
fi

echo "✓ Ejecutando como root"

# Crear archivo de startup
echo "Creando script de startup..."

cat > "$STARTUP_SCRIPT" << 'STARTUP_EOF'
#!/bin/bash
# Script que se ejecuta al iniciar gamecube service
# Rutas configurables debajo ⬇️

# ⚠️  CONFIGURACIÓN DE RUTAS - EDITA SI ES NECESARIO
PROJECT_DIR="/home/pi/proyecto_fse_gamecube"          # 👈 Ruta donde clonaste el proyecto
VIDEO_FILE="$PROJECT_DIR/videos/gamecube.mp4"        # 👈 Video intro (guardar: cp tu_video.mp4 aquí)
VENV_PYTHON="$PROJECT_DIR/env/bin/python3"

cd "$PROJECT_DIR"

# Reproducir video de inicio (si existe)
if [ -f "$VIDEO_FILE" ]; then
    echo "[$(date)] Reproduciendo video de GameCube..."
    timeout 20 omxplayer "$VIDEO_FILE" 2>/dev/null || true
    sleep 1
else
    echo "[$(date)] Video no encontrado (ignorando)"
fi

# Activar venv y ejecutar servidor
echo "[$(date)] Iniciando servidor GameCube..."
source "$PROJECT_DIR/env/bin/activate"
exec python -m uvicorn app:app --host 0.0.0.0 --port 8000
STARTUP_EOF

chmod +x "$STARTUP_SCRIPT"
echo "✓ Script de startup creado en $STARTUP_SCRIPT"

# Crear servicio systemd
echo "Creando servicio systemd..."

cat > "$SYSTEMD_SERVICE" << SYSTEMD_EOF
[Unit]
Description=GameCube - Proyecto Final FSE
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=$PROJECT_DIR
ExecStart=$STARTUP_SCRIPT
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
SYSTEMD_EOF

chmod 644 "$SYSTEMD_SERVICE"
echo "✓ Servicio creado en $SYSTEMD_SERVICE"

# Recargar systemd
systemctl daemon-reload
echo "✓ Systemd recargado"

# Habilitar servicio
systemctl enable gamecube
echo "✓ Servicio habilitado para autostart"

# Crear directorio videos si no existe
mkdir -p "$PROJECT_DIR/videos"
echo "✓ Carpeta videos verificada"

echo ""
echo "======================================================================"
echo "INSTALACIÓN COMPLETADA"
echo "======================================================================"
echo ""
echo "Comandos útiles:"
echo "  Iniciar:   sudo systemctl start gamecube"
echo "  Detener:   sudo systemctl stop gamecube"
echo "  Estado:    sudo systemctl status gamecube"
echo "  Logs:      sudo journalctl -u gamecube -f"
echo "  Deshabilitar autostart: sudo systemctl disable gamecube"
echo ""
echo "El servicio iniciará automáticamente al reiniciar."
echo ""
echo "Para reproducir video al inicio:"
echo "  1. Coloca gamecube.mp4 en: $PROJECT_DIR/videos/"
echo "  2. El video se reproducirá 20 segundos (max) al iniciar"
echo ""
echo "Prueba manual del servicio:"
echo "  sudo systemctl start gamecube"
echo "  Luego abre: http://<IP-RASP>:8000"
echo ""
