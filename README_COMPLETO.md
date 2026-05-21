# 🎮 GameCube - Proyecto Final FSE - SIMON DICE

**Sistema de juegos interactivos basado en Raspberry Pi 4 con interfaz web**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-Educational-green.svg)](#license)

---

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Quick Start](#-quick-start)
- [Instalación](#-instalación)
- [Hardware](#-hardware)
- [Controles](#-controles)
- [Desarrollo](#-desarrollo)
- [Troubleshooting](#-troubleshooting)

---

## ✨ Características

### Modos de Juego
- 🧠 **Memoria (Simon Dice)**: Reproduce y repite secuencias de colores
- 🎵 **Ritmo (Guitar Hero)**: Bloques que caen, 30 segundos de juego continuo

### Hardware
- 🕹️ **8 Botones GPIO**: 4 por jugador (expandible)
- 💡 **4 LEDs**: Feedback visual en tiempo real
- 📱 **LCD I2C 16x2**: Info del juego en vivo
- 🔌 **Pull-up automático**: No necesitas resistencias externas

### Infraestructura
- 🌐 **WebSocket bidireccional**: Comunicación en tiempo real
- 🤖 **Hardware Detection**: Funciona en PC (simulación) o Raspberry Pi (GPIO real)
- ⚡ **FastAPI + Uvicorn**: Servidor ultra-rápido
- 📱 **Responsive**: 720p optimizado, funciona en PC/tablet/móvil

### Multiplayer
- 1️⃣ **Un jugador**: Modo clásico
- 👥 **Dos jugadores**: Modo competitivo con ranking

---

## 🚀 Quick Start

### En Raspberry Pi (la forma más fácil)

```bash
git clone https://github.com/Joel-Lopez-Dev/proyecto_fse_gamecube.git
cd proyecto_fse_gamecube
sudo bash setup-rasp.sh
sudo systemctl start gamecube
```

Luego abre en navegador: **http://<IP-RASP>:8000**

### En PC (Desarrollo)

```bash
git clone https://github.com/Joel-Lopez-Dev/proyecto_fse_gamecube.git
cd proyecto_fse_gamecube
python -m venv env
source env/bin/activate  # Windows: env\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app:app --host 127.0.0.1 --port 8001 --reload
```

Abre: **http://127.0.0.1:8001**

---

## 📦 Instalación

### Instalación Manual (Paso a paso)

Ver: **[INSTALACION.md](INSTALACION.md)** para instrucciones detalladas.

### Instalación Automática (Raspberry Pi)

```bash
sudo bash setup-rasp.sh
```

Esto instala:
- ✓ Dependencias del sistema
- ✓ Python 3 + pip + venv
- ✓ Librerías GPIO (RPi.GPIO, smbus2, rpi-lcd)
- ✓ Servicio systemd para autostart
- ✓ Configuración I2C

---

## ⚙️ Hardware

### Conexiones GPIO

Consulta [CONEXIONES.txt](CONEXIONES.txt) para:
- 🔌 Esquema de pines GPIO
- 💡 Conexión de LEDs (con resistencias)
- 🔘 Conexión de botones
- 📱 Cableado LCD I2C

**Resumen rápido:**

| Componente | Pines | Notas |
|-----------|-------|-------|
| Botones J1 | GPIO 17, 27, 22, 23 | Conectar a GND + pull-up interno |
| Botones J2 | GPIO 24, 25, 4, 14 | Expandible, por ahora sin conectar |
| LEDs | GPIO 5, 6, 13, 26 | Con resistencia 330Ω a GND |
| LCD I2C | SDA/SCL (GPIO 2/3) | Dirección 0x27 |

### Verificar Conexiones

```bash
# Listar dispositivos I2C
sudo i2cdetect -y 1

# Probar un LED
python3 -c "
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(5, GPIO.OUT)
GPIO.output(5, GPIO.HIGH)
print('LED 1 encendido')
"
```

---

## 🎮 Controles

### Teclado (PC)

**Jugador 1 (Memoria/Ritmo):**
- Q → Color 1 (Rojo)
- W → Color 2 (Amarillo)  
- E → Color 3 (Azul)
- R → Color 4 (Verde)

**Jugador 2 (Ritmo):**
- U → Color 1
- I → Color 2
- O → Color 3
- P → Color 4

### Botones Físicos (Raspberry Pi)

Los botones GPIO se mapean automáticamente según las conexiones en [CONEXIONES.txt](CONEXIONES.txt).

---

## 📁 Estructura

```
proyecto_fse_gamecube/
├── app.py                    # Backend FastAPI (580+ líneas)
├── requirements.txt          # Dependencias Python
├── INSTALACION.md           # Guía de instalación detallada
├── CONEXIONES.txt           # Esquema GPIO/LCD
├── README.md                # Este archivo
├── gamecube-autostart.sh    # Script systemd + video intro
├── setup-rasp.sh            # Instalación automática Rasp
├── templates/
│   └── index.html           # Interfaz web (270+ líneas)
├── static/
│   ├── css/
│   │   └── style.css        # Tema GameCube (600+ líneas)
│   └── js/
│       └── game.js          # Lógica frontend (500+ líneas)
└── videos/
    └── gamecube.mp4         # Video intro (opcional)
```

---

## 🖥️ Desarrollo

### Modo Simulación (PC)

Automáticamente detecta que no está en Rasp y:
- Desactiva GPIO real
- Simula LEDs en consola
- Simula LCD con ASCII art
- Los botones se controlan por teclado

### Editar Código

1. **Backend**: Edita `app.py` y recarga (auto con `--reload`)
2. **Frontend**: Edita `templates/index.html` o `static/js/game.js` y recarga navegador
3. **Estilos**: Edita `static/css/style.css` y recarga

### Hot Reload

```bash
python -m uvicorn app:app --host 127.0.0.1 --port 8001 --reload
```

El servidor se reinicia automáticamente al cambiar `app.py`.

---

## 🔄 Autostart (Raspberry Pi)

### Habilitar Autostart

```bash
sudo bash gamecube-autostart.sh
```

Esto:
- Crea un servicio systemd
- Configura para iniciar automáticamente
- Reproduce video intro (si existe)
- Lanza el navegador en fullscreen

### Ver Estado

```bash
sudo systemctl status gamecube
```

### Ver Logs

```bash
sudo journalctl -u gamecube -f
```

### Deshabilitar

```bash
sudo systemctl disable gamecube
```

---

## 📺 Video Intro

1. Coloca `gamecube.mp4` en carpeta `videos/`
2. El script de autostart lo reproducirá 20 segundos al inicio
3. Si no existe, solo inicia el servidor (sin error)

---

## 🎯 Modos de Juego

### Simon Dice (Memoria)

```
1. Elige 1 o 2 jugadores
2. El juego muestra una secuencia de colores (LEDs)
3. Debes repetir la secuencia presionando botones
4. Cada nivel agrega un color más
5. Un error y pierdes
```

**LCD muestra:**
```
Combo: 5
Score: 150
```

### Guitar Hero (Ritmo)

```
1. Elige 1 o 2 jugadores
2. 30 segundos de bloques cayendo
3. Presiona botón cuando llegue a la línea roja
4. Perfecta = 100 pts | Buena = 50 pts | Aceptable = 25 pts
5. Pantalla de resultado con ganador
```

**LCD muestra:**
```
Racha: 8 | 5
J1: 450 | J2: 320
```

---

## ⚙️ API WebSocket

### Eventos Enviados (Cliente → Servidor)

```javascript
// Simon Dice
{type: 'simon_input', player_id: 1, color: 2}

// Guitar Hero
{type: 'guitar_input', player_id: 1, color: 3, accuracy: 0.92}

// Pruebas
{type: 'led_test', led: 1}
{type: 'lcd_write', line1: 'Hola', line2: 'Mundo'}
```

### Eventos Recibidos (Servidor → Cliente)

```javascript
// Feedback Simon
{type: 'simon_feedback', correct: true, score: 100, combo: 5}

// Feedback Guitar
{type: 'guitar_feedback', player_id: 1, result: 'perfect', points: 100, scores: {1: 450, 2: 320}}

// Nueva nota Guitar Hero
{type: 'guitar_spawn', note: {note_id: '...', color: 2, spawn_time: 1234.56}}
```

---

## 🐛 Troubleshooting

| Problema | Solución |
|----------|----------|
| `ModuleNotFoundError: RPi.GPIO` | `pip install RPi.GPIO` |
| Botones no responden | Verifica CONEXIONES.txt + GPIO pins |
| LCD en blanco | `sudo i2cdetect -y 1` → verifica 0x27 |
| Autostart no funciona | `sudo systemctl status gamecube` |
| Permisos denegados | Usa `sudo` o agrega usuario a grupo GPIO |
| Video no se reproduce | Verifica ruta `videos/gamecube.mp4` |

### Debug Mode

```bash
# Logs del servidor
sudo journalctl -u gamecube -f

# Consola del navegador (F12)
# Búsca errores en Network tab (WebSocket)

# Prueba GPIO manualmente
python3 -c "
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
print('GPIO 17:', GPIO.input(17))  # 1=sin presionar, 0=presionado
GPIO.cleanup()
"
```

---

## 📊 Requisitos

### Hardware

- **Raspberry Pi 4** (4GB mínimo recomendado)
- **8 Botones** (pulsadores normales)
- **4 LEDs** + resistencias 330Ω
- **LCD 16x2 I2C**
- **Fuente 5V/3A** (o superior)

### Software

- Python 3.8+
- FastAPI 0.104.1
- Uvicorn 0.24.0
- RPi.GPIO 0.7.0 (solo Rasp)
- smbus2 0.4.2 (solo Rasp)
- rpi-lcd 1.2.2 (solo Rasp)

### Navegador

- Chrome/Chromium (recomendado en Rasp)
- Firefox
- Safari
- Edge

---

## 📝 Licencia

Proyecto educativo | Raspberry Pi 4 (4GB)

---

## 👨‍💻 Desarrollo

- **Inicial**: 0% en PC (CLI y pruebas)
- **Beta**: 100% en Rasp (hardware real)
- **Estado Actual**: Production Ready ✓

---

**Última actualización**: Mayo 2026  
**Versión**: 1.0.0  
**Autor**: Proyecto Final FSE
