# INSTALACIÓN - GAMECUBE PROYECTO FSE

## Quick Start (Rasp)

```bash
git clone https://github.com/Joel-Lopez-Dev/proyecto_fse_gamecube.git
cd proyecto_fse_gamecube
sudo bash setup-rasp.sh
sudo bash gamecube-autostart.sh
```

Eso es todo. El proyecto estará corriendo. 🎮

---

## Instalación Manual (paso a paso)

### 1. Clonar el repositorio

```bash
git clone https://github.com/Joel-Lopez-Dev/proyecto_fse_gamecube.git
cd proyecto_fse_gamecube
```

### 2. Crear entorno virtual

```bash
python3 -m venv env
source env/bin/activate
```

### 3. Instalar dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

En Raspberry Pi, también instala las librerías de hardware:

```bash
pip install RPi.GPIO smbus2 rpi-lcd
```

### 4. Verificar conexiones

**Antes de ejecutar**, verifica que los botones y LEDs estén conectados según `CONEXIONES.txt`.

### 5. Ejecutar el servidor

**En desarrollo (PC)**:
```bash
python -m uvicorn app:app --host 127.0.0.1 --port 8001 --reload
```
Luego abre http://127.0.0.1:8001

**En Raspberry Pi**:
```bash
sudo python -m uvicorn app:app --host 0.0.0.0 --port 8000
```
Abre http://<IP-RASP>:8000 en otro dispositivo

---

## Estructura del Proyecto

```
proyecto_fse_gamecube/
├── app.py                    # Backend FastAPI
├── requirements.txt          # Dependencias Python
├── CONEXIONES.txt           # Esquema GPIO/LCD
├── INSTALACION.md           # Este archivo
├── gamecube-autostart.sh    # Script de autostart
├── setup-rasp.sh            # Script instalación Rasp
├── templates/
│   └── index.html           # Interfaz web
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── game.js
└── videos/
    └── gamecube.mp4         # Intro (opcional)
```

---

## Autostart (Ejecutar automáticamente al iniciar Rasp)

El script `gamecube-autostart.sh` hace todo:

```bash
sudo bash gamecube-autostart.sh
```

Esto:
- Crea un servicio systemd
- Habilita autostart al iniciar Rasp
- Intenta reproducir `videos/gamecube.mp4` al inicio
- Lanza el servidor automáticamente
- Abre el navegador en fullscreen

**Para deshabilitar autostart**:
```bash
sudo systemctl disable gamecube
```

**Para ver logs**:
```bash
sudo journalctl -u gamecube -f
```

---

## Configuración LCD I2C

Si el LCD no funciona, verifica su dirección I2C:

```bash
sudo i2cdetect -y 1
```

Busca un dispositivo (normalmente en 0x27). Si está en otra dirección, edita `app.py`:

```python
LCD_ADDRESS = 0x27  # Cambia aquí
```

---

## Modo Configuración

Accede a **Configuración** en el menú para:
- Seleccionar 1 o 2 jugadores
- Ver estado de conexión
- Probar LEDs
- Ver información del hardware

---

## Solución de Problemas

### "ModuleNotFoundError: No module named 'RPi.GPIO'"

```bash
pip install RPi.GPIO
```

### "Error: Intento de acceso a un socket no permitido"

```bash
sudo python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

### Botones no responden

1. Verifica CONEXIONES.txt
2. Prueba un botón manual:
```bash
python3 -c "
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
while True:
    print(GPIO.input(17))
"
```

### LCD en blanco

```bash
sudo i2cdetect -y 1
```

Si no aparece nada en 0x27, verifica cableado I2C.

---

## Desarrollo en PC

Para desarrollar en Windows/Mac sin Rasp:

```bash
python -m uvicorn app:app --host 127.0.0.1 --port 8001 --reload
```

Automáticamente entrará en **SIMULATION MODE** (sin hardware real).

---

## Actualizar código

```bash
git pull origin main
sudo systemctl restart gamecube
```

---

**¡Listo!** Si todo funciona, deberías ver el menú en http://<IP-RASP>:8000 🎮
