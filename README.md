# GAMECUBE - Proyecto Final FSE - SIMON DICE

Sistema de videojuegos interactivos basado en **FastAPI + WebSockets** para Raspberry Pi 4, con desarrollo inicial en PC.

## Características

### Modos de Juego
- **Memoria**: Clásico juego de memoria. LEDs físicos en Raspberry Pi, pantalla web ciega.
- **Ritmo**: Notas cayendo en pantalla web con timing crucial (1 minuto de juego).

### Infraestructura
- **PC Fallback Inteligente**: Detecta automáticamente si está en Raspberry Pi o PC. En PC, los LEDs y LCD se simulan en consola.
- **Arquitectura Ultra-Lite**: FastAPI + WebSockets asíncrono = ideal para Rasp 4GB sin lag.
- **LCD I2C Dinámico**: Muestra rachas, puntajes, líder en tiempo real.
- **Soporte Futuro Jugador 3**: Estructura JSON lista para recibir inputs de Arduino vía Bluetooth.

### Estética
- **Tema Xbox**: Negro mate (#0d0d0d) + Verde fosforescente (#107C10)
- **Controles PC**: Teclado QWER (J1) y UIOP (J2)
- **Responsivo**: Funciona en PC, tablet y móvil

## 🚀 Instalación Rápida (PC - Windows/macOS)

### Paso 1: Crear Entorno Virtual
```bash
cd simon_xbox_project
python -m venv env
source env/Scripts/activate  # Windows: env\Scripts\activate
```

### Paso 2: Instalar Dependencias
```bash
pip install fastapi uvicorn websockets
```

### Paso 3: Ejecutar el Servidor
```bash
python app.py
```

### Paso 4: Abrir en Navegador
```
http://localhost:8000
```

## 📁 Estructura del Proyecto

```
simon_xbox_project/
├── app.py                          # Backend FastAPI + Hardware Mocks
├── requirements.txt                # Dependencias Python
├── README.md                       # Este archivo
├── templates/
│   └── index.html                  # Interfaz web Xbox
└── static/
    ├── css/
    │   └── style.css               # Estilos negro/verde fosforescente
    └── js/
        └── game.js                 # Lógica WebSocket + Teclado QWER/UIOP
```

## 🎮 Controles

### En PC (Teclado)
```
Jugador 1:  Q(Rojo) | W(Cyan) | E(Amarillo) | R(Púrpura)
Jugador 2:  U(Rojo) | I(Cyan) | O(Amarillo) | P(Púrpura)
```

### En Raspberry Pi (Botones Físicos)
- Pin GPIO 17: Botón 1 (Rojo)
- Pin GPIO 27: Botón 2 (Cyan)
- Pin GPIO 22: Botón 3 (Amarillo)
- Pin GPIO 23: Botón 4 (Púrpura)

### LEDs Indicadores
- Pin GPIO 5: LED 1
- Pin GPIO 6: LED 2
- Pin GPIO 13: LED 3
- Pin GPIO 26: LED 4

## 🔧 Modo Simulación (PC)

Cuando se ejecuta en PC, el código automáticamente:

1. **LEDs**: Muestra en consola qué LED se encendería
   ```
   [HH:MM:SS.fff] LED1: 🟢
   [HH:MM:SS.fff] LED1: ⚫
   ```

2. **LCD I2C**: Simula pantalla LCD en la terminal
   ```
   [LCD] ┌────────────────┐
         │Xbox Arcade     │
         │Listo! Sim      │
         └────────────────┘
   ```

3. **WebSocket**: Funciona normalmente con conexión en `ws://localhost:8000/ws`

## 📡 API WebSocket

### Eventos Disponibles

#### Simon Dice
```javascript
// Iniciar
{ type: "simon_start", player_count: 1 }

// Input del usuario
{ type: "simon_input", player_id: 1, color: 3 }

// Respuesta del servidor
{
  type: "simon_feedback",
  correct: true,
  combo: 5,
  score: 50,
  message: "¡Acierto #3!"
}
```

#### Guitar Hero
```javascript
// Iniciar
{ type: "guitar_start", player_count: 1 }

// Input del usuario (accuracy: 0.0-1.0)
{ type: "guitar_input", player_id: 1, color: 2, accuracy: 0.95 }

// Respuesta del servidor
{
  type: "guitar_feedback",
  result: "perfect",
  points: 100,
  combo: 5,
  score: 250
}
```

#### Hardware
```javascript
// Test LED
{ type: "led_test", led_num: 1 }

// Escribir LCD
{ type: "lcd_write", line1: "Hola", line2: "Mundo" }

// Futuro: Input Jugador 3 (Bluetooth/Arduino)
{ type: "player3_input", color: 2, accuracy: 0.8 }
```

## 🛠️ Transferencia a Raspberry Pi

### Preparación en Rasp
```bash
# Actualizar sistema
sudo apt-get update && sudo apt-get upgrade -y

# Instalar Python y pip
sudo apt-get install python3 python3-pip python3-venv

# Instalar dependencias del sistema para GPIO
sudo apt-get install python3-rpi.gpio python3-smbus i2c-tools

# Clonar/copiar proyecto
git clone https://github.com/tuusuario/simon-xbox-project.git
cd simon-xbox-project

# Crear entorno virtual
python3 -m venv env
source env/bin/activate

# Instalar requirements
pip install -r requirements.txt

# Ejecutar en puerto 80 (requiere sudo)
sudo env/bin/python app.py
```

### Configuración de Autostart (Systemd)
```bash
sudo nano /etc/systemd/system/xbox-arcade.service
```

```ini
[Unit]
Description=Xbox Arcade Gaming Server
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/simon-xbox-project
ExecStart=/home/pi/simon-xbox-project/env/bin/python app.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable xbox-arcade.service
sudo systemctl start xbox-arcade.service
```

## 🔌 Diagrama de Hardware (Raspberry Pi)

```
                     [Raspberry Pi 4B]
                           |
    ┌──────────────────────┼──────────────────────┐
    |                      |                      |
 [GPIO]                 [I2C Bus]            [Botones]
    |                      |                      |
 LED1-4 (5,6,13,26)   LCD 0x27              (17,27,22,23)
```

## 📊 Scoring

### Memoria
- Cada acierto: +10 puntos
- Racha (combo): Aumenta por cada acierto consecutivo
- Error: Racha se reinicia

### Ritmo (1 minuto)
- **Perfect** (>95% accuracy): 100 pts + 5 combo
- **Great** (>85% accuracy): 50 pts + 2 combo
- **Good** (>70% accuracy): 25 pts + 1 combo
- **Miss**: 0 pts, racha a 0

## 🐛 Troubleshooting

| Problema | Solución |
|----------|----------|
| `ModuleNotFoundError: No module named 'fastapi'` | Ejecutar `pip install -r requirements.txt` |
| `Address already in use` | Cambiar puerto en `uvicorn.run(port=8001)` |
| LEDs/LCD no funcionan | Revisar modo simulación en consola. En Rasp, verificar permisos GPIO |
| WebSocket no conecta | Verificar firewall, intentar acceder a `http://localhost:8000/health` |
| Notas Guitar Hero no se renderizan | Actualizar navegador (requiere ES6 + Canvas API) |

## 📱 Soporte Futuro (Jugador 3 Bluetooth)

Estructura JSON lista en `app.py` para recibir inputs de Arduino vía Bluetooth:

```python
elif event_type == "player3_input":
    if 3 not in engine.players:
        engine.players[3] = {"score": 0, "combo": 0, "errors": 0}
    # ... procesa input P3
```

El LCD automáticamente incluirá la racha de P3.

## 🎨 Personalización

### Cambiar Colores
Editar `:root` en `static/css/style.css`:
```css
--xbox-green: #107C10;  /* Cambiar color principal */
--xbox-dark: #0a0e27;
```

### Cambiar Velocidad Guitar Hero
En `static/js/game.js`:
```javascript
const speed = 150; // píxeles por segundo (cambiar aquí)
```

### Cambiar Tamaño LCD
En `app.py`:
```python
LCD_COLS = 16  # Cambiar si tu LCD es 20x4
LCD_ROWS = 2
```

## 📞 Soporte

Para dudas o problemas:
1. Revisar consola del navegador (F12 → Console)
2. Revisar terminal donde se ejecuta `app.py`
3. Probar modo simulación en PC primero
4. Validar conexión WebSocket en `/health` endpoint

## 📜 Licencia

Este proyecto es demostrativo y educativo. Libre para uso personal y educativo.

---

**Construido con ❤️ para Raspberry Pi 4 en Xbox Series X**

🚀 Disfruta tu arcade interactivo personal.
