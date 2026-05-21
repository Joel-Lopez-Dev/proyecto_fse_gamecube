"""
FastAPI Backend: GameCube - Proyecto Final FSE - SIMON DICE
Memoria + Ritmo con Hardware Mocks
"""

import asyncio
import random
import json
import time
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
from typing import Dict, List

# ============================================================================
# DETECCIÓN DE HARDWARE Y MOCKS
# ============================================================================

SIMULATION_MODE = False
# GPIO PINS - 8 botones (4 J1 + 4 J2) + 4 LEDs
GPIO_PINS = {
    # Botones Jugador 1
    "btn1_j1": 17, "btn2_j1": 27, "btn3_j1": 22, "btn4_j1": 23,
    # Botones Jugador 2 (preparados para expandir)
    "btn1_j2": 24, "btn2_j2": 25, "btn3_j2": 4, "btn4_j2": 14,
    # LEDs (4 para colores de notas)
    "led1": 5, "led2": 6, "led3": 13, "led4": 26
}
LCD_ADDRESS = 0x27
LCD_COLS = 16
LCD_ROWS = 2

class HardwareManager:
    """Gestor de GPIO y LCD con fallback a simulación."""
    
    def __init__(self):
        global SIMULATION_MODE
        self.simulation_mode = True
        self.leds_state = {f"led{i}": False for i in range(1, 5)}
        
        try:
            import RPi.GPIO as GPIO
            import smbus2
            from rpi_lcd import CharLCD
            
            self.gpio = GPIO
            self.smbus = smbus2
            self.CharLCD = CharLCD
            self.simulation_mode = False
            SIMULATION_MODE = False
            
            # Configurar GPIO
            self.gpio.setmode(self.gpio.BCM)
            for pin_name, pin_num in GPIO_PINS.items():
                if "led" in pin_name:
                    self.gpio.setup(pin_num, self.gpio.OUT)
                    self.gpio.output(pin_num, self.gpio.LOW)
            
            # Inicializar LCD
            self.lcd = self.CharLCD(address=LCD_ADDRESS, cols=LCD_COLS, rows=LCD_ROWS)
            self.lcd.clear()
            
            print("OK - Hardware real detectado en Raspberry Pi")
        
        except (ImportError, RuntimeError) as e:
            self.simulation_mode = True
            SIMULATION_MODE = True
            print("SIMULACION - Librerías de hardware no disponibles")
            print(f"  Razón: {type(e).__name__}")
    
    def set_led(self, led_num: int, state: bool):
        """Encender/apagar LED."""
        led_key = f"led{led_num}"
        self.leds_state[led_key] = state
        
        if not self.simulation_mode:
            pin = GPIO_PINS[led_key]
            state_val = self.gpio.HIGH if state else self.gpio.LOW
            self.gpio.output(pin, state_val)
        
        symbol = "[ON]" if state else "[OFF]"
        print(f"  [{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] LED{led_num}: {symbol}")
    
    def write_lcd(self, line1: str = "", line2: str = ""):
        """Escribir en LCD I2C."""
        line1 = (line1[:LCD_COLS]).ljust(LCD_COLS)
        line2 = (line2[:LCD_COLS]).ljust(LCD_COLS)
        
        if not self.simulation_mode:
            self.lcd.clear()
            self.lcd.write_string(line1)
            self.lcd.crlf()
            self.lcd.write_string(line2)
        
        print(f"  [LCD] ┌{'─' * LCD_COLS}┐")
        print(f"        │{line1}│")
        print(f"        │{line2}│")
        print(f"        └{'─' * LCD_COLS}┘")
    
    def cleanup(self):
        """Limpiar recursos."""
        if not self.simulation_mode:
            self.gpio.cleanup()
            self.lcd.clear()

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

async def spawn_guitar_notes_loop(game_engine, player_count, manager):
    """Genera notas de Guitar Hero cada 300ms durante 30 segundos"""
    start_time = time.time()
    duration = 30  # 30 segundos
    spawn_interval = 0.3  # 300ms
    
    while time.time() - start_time < duration:
        for p in range(1, player_count + 1):
            note = game_engine.spawn_guitar_note(p)
            await manager.broadcast({
                "type": "guitar_spawn",
                "note": note
            })
        await asyncio.sleep(spawn_interval)

# ============================================================================
# LÓGICA DEL JUEGO
# ============================================================================

class GameEngine:
    """Motor de juego: Memoria (Simon) y Ritmo (Guitar Hero)."""
    
    def __init__(self, hw: HardwareManager):
        self.hw = hw
        self.players = {}
        self.current_mode = None  # "simon" o "guitar"
        self.simon_sequence = []
        self.simon_step = 0
        self.guitar_combo = {1: 0, 2: 0}
        self.guitar_active_notes = {}
        
    def reset_game(self, mode: str, player_count: int = 1):
        """Reiniciar juego."""
        self.current_mode = mode
        self.players = {i: {"score": 0, "combo": 0, "errors": 0} for i in range(1, player_count + 1)}
        
        if mode == "simon":
            self.simon_sequence = []
            self.simon_step = 0
            self.add_simon_step()
        elif mode == "guitar":
            self.guitar_combo = {i: 0 for i in range(1, player_count + 1)}
            self.guitar_active_notes = {}
    
    def add_simon_step(self):
        """Agregar paso aleatorio a la secuencia Simon."""
        new_color = random.randint(1, 4)
        self.simon_sequence.append(new_color)
        self.simon_step = 0
    
    def play_simon_sequence_led(self):
        """Reproducir secuencia de LEDs con delays."""
        async def _animate():
            for color in self.simon_sequence:
                self.hw.set_led(color, True)
                await asyncio.sleep(0.6)
                self.hw.set_led(color, False)
                await asyncio.sleep(0.2)
        
        return _animate()
    
    def check_simon_input(self, player_id: int, color: int) -> Dict:
        """Validar input Simon Dice."""
        if color != self.simon_sequence[self.simon_step]:
            self.players[player_id]["errors"] += 1
            self.players[player_id]["combo"] = 0
            self.hw.write_lcd(f"Error! E:{self.players[player_id]['errors']}", f"Puntuación: {self.players[player_id]['score']}")
            return {"correct": False, "message": "¡Error! Secuencia rota.", "combo": 0}
        
        self.simon_step += 1
        self.players[player_id]["combo"] += 1
        self.players[player_id]["score"] += 10
        
        if self.simon_step >= len(self.simon_sequence):
            self.add_simon_step()
            return {"correct": True, "message": "¡Nivel siguiente!", "level": len(self.simon_sequence), "combo": self.players[player_id]["combo"]}
        
        return {"correct": True, "message": f"Acierto #{self.simon_step}", "combo": self.players[player_id]["combo"]}
    
    def spawn_guitar_note(self, player_id: int) -> Dict:
        """Generar nota para Guitar Hero."""
        note_id = f"p{player_id}_{datetime.now().timestamp()}"
        color = random.randint(1, 4)
        
        self.guitar_active_notes[note_id] = {
            "player": player_id,
            "color": color,
            "spawn_time": datetime.now().timestamp(),
            "status": "falling"
        }
        
        return {"note_id": note_id, "color": color, "spawn_time": datetime.now().timestamp()}
    
    def check_guitar_input(self, player_id: int, color: int, accuracy: float) -> Dict:
        """Validar input Guitar Hero basado en timing."""
        # accuracy: 0.0-1.0 (1.0 = perfect, 0.0 = miss)
        result = "miss"
        points = 0
        
        if accuracy > 0.95:
            result = "perfect"
            points = 100
            self.guitar_combo[player_id] += 5
        elif accuracy > 0.85:
            result = "great"
            points = 50
            self.guitar_combo[player_id] += 2
        elif accuracy > 0.7:
            result = "good"
            points = 25
            self.guitar_combo[player_id] += 1
        else:
            self.guitar_combo[player_id] = 0
        
        self.players[player_id]["score"] += points
        self.players[player_id]["combo"] = self.guitar_combo[player_id]
        
        # Feedback en LCD
        leader = max(self.guitar_combo, key=self.guitar_combo.get)
        self.hw.write_lcd(
            f"Racha: {self.guitar_combo[1]:3d} | {self.guitar_combo[2]:3d}" if 2 in self.guitar_combo else f"Combo: {self.guitar_combo[1]:5d}",
            f"J1:{self.players[1]['score']:5d} | J2:{self.players[2]['score']:5d}" if 2 in self.players else f"Score: {self.players[1]['score']:6d}"
        )
        
        return {"result": result, "points": points, "combo": self.guitar_combo[player_id]}

# ============================================================================
# APP FASTAPI
# ============================================================================

app = FastAPI(title="GameCube FSE", docs_url=None, redoc_url=None)

# Servir archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Instanciar hardware y juego
hw = HardwareManager()
engine = GameEngine(hw)

# Almacenar conexiones WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, data: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(data)
            except:
                pass

manager = ConnectionManager()

# ============================================================================
# RUTAS HTTP
# ============================================================================

@app.get("/")
async def serve_index():
    """Servir página principal."""
    return FileResponse("templates/index.html", media_type="text/html")

@app.get("/health")
async def health_check():
    """Health check del servidor."""
    return {
        "status": "ok",
        "simulation_mode": SIMULATION_MODE,
        "timestamp": datetime.now().isoformat()
    }

# ============================================================================
# WEBSOCKET
# ============================================================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket para comunicación bidireccional juego."""
    await manager.connect(websocket)
    
    try:
        # Enviar estado inicial
        await websocket.send_json({
            "type": "init",
            "simulation_mode": SIMULATION_MODE,
            "message": "Conectado a GameCube"
        })
        
        while True:
            data = await websocket.receive_json()
            event_type = data.get("type")
            
            # ========== EVENTOS SIMON DICE ==========
            if event_type == "simon_start":
                player_count = data.get("player_count", 1)
                engine.reset_game("simon", player_count)
                await manager.broadcast({
                    "type": "simon_ready",
                    "message": "¡Secuencia iniciada!",
                    "level": 1
                })
                # Reproducir primera secuencia
                await engine.play_simon_sequence_led()
                await manager.broadcast({"type": "simon_show_ready"})
            
            elif event_type == "simon_input":
                player_id = data.get("player_id", 1)
                color = data.get("color")
                
                result = engine.check_simon_input(player_id, color)
                await manager.broadcast({
                    "type": "simon_feedback",
                    "correct": result["correct"],
                    "combo": result["combo"],
                    "score": engine.players[player_id]["score"],
                    "message": result["message"]
                })
                
                if result["correct"] and engine.simon_step == 0:
                    # Reproducir siguiente nivel
                    await asyncio.sleep(1)
                    await engine.play_simon_sequence_led()
                    await manager.broadcast({"type": "simon_show_ready"})
            
            # ========== EVENTOS GUITAR HERO ==========
            elif event_type == "guitar_start":
                player_count = data.get("player_count", 1)
                engine.reset_game("guitar", player_count)
                await manager.broadcast({
                    "type": "guitar_ready",
                    "message": "¡A ritmo! 30 segundos",
                    "players": player_count
                })
                
                # Spawn notas continuamente durante 30 segundos
                asyncio.create_task(spawn_guitar_notes_loop(engine, player_count, manager))
            
            elif event_type == "guitar_spawn":
                player_id = data.get("player_id", 1)
                note = engine.spawn_guitar_note(player_id)
                await manager.broadcast({
                    "type": "guitar_spawn",
                    "note": note
                })
            
            elif event_type == "guitar_input":
                player_id = data.get("player_id", 1)
                color = data.get("color")
                accuracy = data.get("accuracy", 0.5)
                
                result = engine.check_guitar_input(player_id, color, accuracy)
                
                # Enviar scores de ambos jugadores para sincronización
                all_scores = {
                    1: engine.players[1]["score"],
                    2: engine.players[2]["score"] if 2 in engine.players else 0
                }
                
                await manager.broadcast({
                    "type": "guitar_feedback",
                    "player_id": player_id,
                    "result": result["result"],
                    "points": result["points"],
                    "combo": result["combo"],
                    "scores": all_scores
                })
            
            # ========== EVENTOS LCD GENERALES ==========
            elif event_type == "lcd_write":
                line1 = data.get("line1", "")
                line2 = data.get("line2", "")
                hw.write_lcd(line1, line2)
            
            # ========== JUGADOR 3 BLUETOOTH (FUTURO) ==========
            elif event_type == "player3_input":
                if 3 not in engine.players:
                    engine.players[3] = {"score": 0, "combo": 0, "errors": 0}
                
                player_id = 3
                color = data.get("color")
                
                if engine.current_mode == "simon":
                    result = engine.check_simon_input(player_id, color)
                elif engine.current_mode == "guitar":
                    accuracy = data.get("accuracy", 0.5)
                    result = engine.check_guitar_input(player_id, color, accuracy)
                
                await manager.broadcast({
                    "type": f"{engine.current_mode}_feedback_p3",
                    "data": result,
                    "player": 3
                })
            
            # ========== COMANDO GENÉRICO LED ==========
            elif event_type == "led_test":
                led_num = data.get("led_num", 1)
                hw.set_led(led_num, True)
                await asyncio.sleep(0.5)
                hw.set_led(led_num, False)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Cliente desconectado")

# ============================================================================
# STARTUP/SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup():
    """Iniciar aplicación."""
    print("\n" + "="*70)
    print("  GAMECUBE - Proyecto Final FSE - SIMON DICE")
    print("="*70)
    hw.write_lcd("GameCube", "Iniciando...")
    await asyncio.sleep(1)
    hw.write_lcd("Listo!", f"{'Sim' if SIMULATION_MODE else 'HW'}")

@app.on_event("shutdown")
async def shutdown():
    """Limpiar al apagar."""
    hw.cleanup()
    print("OK - Recursos liberados")

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("\n⚡ Iniciando servidor...")
    print("   http://localhost:8000")
    print("   ws://localhost:8000/ws\n")
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="critical"
    )
