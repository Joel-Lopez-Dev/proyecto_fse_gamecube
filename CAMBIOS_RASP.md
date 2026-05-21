# CAMBIOS PARA RASPBERRY PI

## Resumen de Adaptaciones (Mayo 2026)

Este documento resume todos los cambios realizados para optimizar el código para Raspberry Pi 4 mientras se mantiene compatibilidad con PC.

---

## 1. Configuración GPIO (app.py)

### Antes
```python
GPIO_PINS = {"btn1": 17, "btn2": 27, "btn3": 22, "btn4": 23, "led1": 5, "led2": 6, "led3": 13, "led4": 26}
```

### Después
```python
GPIO_PINS = {
    # Botones Jugador 1
    "btn1_j1": 17, "btn2_j1": 27, "btn3_j1": 22, "btn4_j1": 23,
    # Botones Jugador 2 (expandible)
    "btn1_j2": 24, "btn2_j2": 25, "btn3_j2": 4, "btn4_j2": 14,
    # LEDs
    "led1": 5, "led2": 6, "led3": 13, "led4": 26
}
```

**Cambio**: Ahora soporta 8 botones (4 por jugador). Rasp detecta automáticamente cuáles están disponibles.

---

## 2. Detección de Hardware

**Sin cambios requeridos** - La lógica existente ya:
- ✓ Intenta importar RPi.GPIO
- ✓ Cae a simulación en PC automáticamente
- ✓ Funciona en ambos entornos sin modificar código

---

## 3. Scripts de Instalación (NUEVOS)

### setup-rasp.sh
Instalación automática one-command:
```bash
sudo bash setup-rasp.sh
```

Instala:
- Dependencias del sistema (python3, pip, venv, i2c-tools, omxplayer)
- Entorno virtual Python
- Paquetes Python (FastAPI, uvicorn, websockets, RPi.GPIO, smbus2, rpi-lcd)
- Habilitación de I2C
- Configuración de autostart

### gamecube-autostart.sh
Servicio systemd que:
- Reproduce video `videos/gamecube.mp4` (si existe)
- Inicia el servidor FastAPI
- Permite autostart con `sudo reboot`

---

## 4. Documentación (NUEVA)

### CONEXIONES.txt
Esquema completo GPIO con:
- Pines para 8 botones
- Pines para 4 LEDs (con resistencias)
- Conexión LCD I2C
- Mensajes LCD por sección
- Notas de cableado

### INSTALACION.md
Guía paso a paso:
- Quick Start (comando único)
- Instalación manual
- Configuración LCD
- Autostart
- Troubleshooting

### README_COMPLETO.md
Documentación completa del proyecto con:
- Características
- Hardware
- Controles
- API WebSocket
- Troubleshooting avanzado

---

## 5. Optimizaciones para Rasp

### Puerto de Escucha
- **PC**: `127.0.0.1:8001` (localhost)
- **Rasp**: `0.0.0.0:8000` (accesible en red)

*Configurar en uvicorn al ejecutar según el entorno*

### Recursos
- ✓ Usar `--reload` solo en desarrollo
- ✓ GPIO pull-up interno (sin resistencias en botones)
- ✓ LCD I2C automático (sin configuración adicional)
- ✓ WebSocket bidireccional (ya optimizado)

### Autostart
```bash
sudo systemctl start gamecube
sudo systemctl status gamecube
sudo systemctl stop gamecube
```

---

## 6. Estructura de Carpetas

```
proyecto_fse_gamecube/
├── app.py                   # Sin cambios (GPIO dinámico)
├── requirements.txt         # Sin cambios
├── templates/
│   └── index.html          # Sin cambios
├── static/
│   ├── css/style.css       # Sin cambios
│   └── js/game.js          # Sin cambios
├── CONEXIONES.txt          # NUEVO - Esquema GPIO
├── INSTALACION.md          # NUEVO - Guía
├── README_COMPLETO.md      # NUEVO - Docs completas
├── gamecube-autostart.sh   # NUEVO - Systemd service
├── setup-rasp.sh           # NUEVO - Auto install
├── CAMBIOS_RASP.md         # NUEVO - Este archivo
└── videos/                 # NUEVA - Carpeta para intro
    └── gamecube.mp4        # Poner aquí el video
```

---

## 7. Flujo de Instalación en Rasp

```
1. git clone https://github.com/Joel-Lopez-Dev/proyecto_fse_gamecube.git
2. cd proyecto_fse_gamecube
3. sudo bash setup-rasp.sh          ← Instala TODO automáticamente
4. (Opcional) cp video.mp4 videos/gamecube.mp4
5. sudo systemctl start gamecube    ← Inicia el servidor
6. Abre: http://<IP-RASP>:8000 en navegador
```

---

## 8. Verificaciones Antes de Usar

### Conexiones Físicas
- [ ] Botones J1 en GPIO 17, 27, 22, 23
- [ ] LEDs con resistencias 330Ω
- [ ] LCD I2C conectado en SDA/SCL
- [ ] GND comunes en todo

### Software
- [ ] I2C habilitado: `sudo raspi-config`
- [ ] RPi.GPIO instalado: `pip list | grep RPi.GPIO`
- [ ] Servidor corre: `sudo systemctl status gamecube`

### Testing
```bash
# Ver dispositivos I2C
sudo i2cdetect -y 1

# Probar LED
python3 test_led.py

# Ver logs del servidor
sudo journalctl -u gamecube -f
```

---

## 9. Diferencias PC vs Rasp

| Aspecto | PC | Rasp |
|--------|----|----|
| GPIO | Simulado (consola) | Real (RPi.GPIO) |
| LEDs | ASCII art | GPIO output |
| LCD | ASCII box | I2C protocol |
| Botones | Teclado | GPIO input |
| Puerto | 8001 | 8000 |
| Autostart | N/A | systemd |
| Video | N/A | omxplayer |

---

## 10. Próximos Pasos (Fase 2)

- [ ] Agregar botones J2 cuando se adquieran
- [ ] Optimizar timings de juego para Rasp
- [ ] Agregar resistencias pull-down en botones (opcional)
- [ ] Crear interfaz de calibración de LCD
- [ ] Script de monitoreo de hardware

---

## 11. Soporte

Si algo falla:

1. Verifica CONEXIONES.txt
2. Lee INSTALACION.md (Troubleshooting)
3. Comprueba logs: `sudo journalctl -u gamecube -f`
4. Prueba GPIO directamente: `python3 -c "import RPi.GPIO as GPIO"`

---

**Estado**: ✅ Listo para Rasp 4  
**Fecha**: Mayo 2026  
**Versión**: 1.0.0
