/* ===================================================================
   XBOX ARCADE GAMING - FRONTEND JAVASCRIPT
   WebSocket, Teclado QWER/UIOP, Guitar Hero Notes
   =================================================================== */

class XboxArcadeGame {
    constructor() {
        // Estado de conexión
        this.ws = null;
        this.connected = false;
        this.simulationMode = false;

        // Estado del juego
        this.currentGame = null; // "simon", "guitar", null
        this.players = {
            1: { score: 0, combo: 0, errors: 0, button: null },
            2: { score: 0, combo: 0, errors: 0, button: null }
        };

        // Simon Dice
        this.simonLevel = 1;
        this.simonCombo = 0;
        this.simonSequence = [];
        this.playerCount = 1;

        // Guitar Hero
        this.guitarNotes = {};
        this.guitarStartTime = 0;
        this.guitarRunning = false;
        this.guitarCombo = { 1: 0, 2: 0 };
        this.guitarTimeLeft = 60;
        this.guitarTimerInterval = null;
        this.guitarNoteInterval = null;
        this.impactLineY = 500; // Altura de la línea de impacto
        this.noteHeight = 60;
        this.canvasContext = null;

        // Mapeo de teclado
        this.keyMap = {
            'q': { color: 1, player: 1 },
            'w': { color: 2, player: 1 },
            'e': { color: 3, player: 1 },
            'r': { color: 4, player: 1 },
            'u': { color: 1, player: 2 },
            'i': { color: 2, player: 2 },
            'o': { color: 3, player: 2 },
            'p': { color: 4, player: 2 }
        };

        this.init();
    }

    // ===================================================================
    // INICIALIZACIÓN
    // ===================================================================

    init() {
        console.log('GameCube - Proyecto Final FSE - SIMON DICE inicializando...');
        this.setupWebSocket();
        this.setupEventListeners();
        this.showSection('menu');
        this.getCanvasContext();
    }

    setupWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const url = `${protocol}//${window.location.host}/ws`;

        this.ws = new WebSocket(url);

        this.ws.onopen = () => {
            console.log('Conectado al servidor');
            this.setConnectionStatus(true);
            this.showToast('Conectado al servidor', 'success');
        };

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
        };

        this.ws.onerror = (error) => {
            console.error('✗ Error WebSocket:', error);
            this.showToast('Error de conexión', 'error');
        };

        this.ws.onclose = () => {
            console.log('✗ WebSocket desconectado');
            this.setConnectionStatus(false);
            this.showToast('Desconectado del servidor', 'error');
        };
    }

    setupEventListeners() {
        // Menú principal
        document.getElementById('btn-simon')?.addEventListener('click', () => this.showSection('simon'));
        document.getElementById('btn-guitar')?.addEventListener('click', () => this.showSection('guitar'));
        document.getElementById('btn-test')?.addEventListener('click', () => this.showSection('test'));

        // Simon Dice
        document.getElementById('simon-start-1p')?.addEventListener('click', () => this.startSimon(1));
        document.getElementById('simon-start-2p')?.addEventListener('click', () => this.startSimon(2));
        document.getElementById('simon-reset')?.addEventListener('click', () => this.resetGame());
        document.getElementById('btn-return-menu')?.addEventListener('click', () => this.returnToMenu());

        // Guitar Hero
        document.getElementById('guitar-start-1p')?.addEventListener('click', () => this.startGuitar(1));
        document.getElementById('guitar-start-2p')?.addEventListener('click', () => this.startGuitar(2));
        document.getElementById('guitar-reset')?.addEventListener('click', () => this.resetGame());
        document.getElementById('btn-return-menu2')?.addEventListener('click', () => this.returnToMenu());

        // Result Modal
        document.getElementById('result-restart')?.addEventListener('click', () => this.hideResultModal());
        document.getElementById('result-menu')?.addEventListener('click', () => this.returnToMenu());

        // Hardware Test
        document.getElementById('btn-return-menu3')?.addEventListener('click', () => this.returnToMenu());
        document.getElementById('btn-lcd-write')?.addEventListener('click', () => this.testLCD());

        // Test LEDs
        document.querySelectorAll('[data-led]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const ledNum = parseInt(e.target.dataset.led);
                this.testLED(ledNum);
            });
        });

        // Botones de juego
        document.querySelectorAll('.btn[data-color]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                if (!this.currentGame) return;
                const color = parseInt(e.target.dataset.color);
                const player = parseInt(e.target.dataset.player) || 1;
                this.handleButtonPress(color, player);
            });
        });

        // Teclado
        document.addEventListener('keydown', (e) => {
            const key = e.key.toLowerCase();
            if (this.keyMap[key]) {
                e.preventDefault();
                const { color, player } = this.keyMap[key];
                this.handleButtonPress(color, player);
            }
        });
    }

    getCanvasContext() {
        const canvas = document.getElementById('guitar-canvas');
        if (canvas) {
            this.canvasContext = canvas.getContext('2d');
        }
    }

    // ===================================================================
    // GESTIÓN DE SECCIONES
    // ===================================================================

    showSection(sectionName) {
        // Ocultar todas las secciones
        document.querySelectorAll('.game-section').forEach(section => {
            section.classList.add('hidden');
        });

        // Mostrar sección específica
        const section = document.getElementById(`${sectionName}-section`);
        if (section) {
            section.classList.remove('hidden');
        }

        this.currentGame = sectionName === 'menu' ? null : sectionName;
        this.updateModeDisplay();
    }

    returnToMenu() {
        this.currentGame = null;
        this.guitarRunning = false;
        if (this.guitarTimerInterval) {
            clearInterval(this.guitarTimerInterval);
        }
        if (this.guitarNoteInterval) {
            clearInterval(this.guitarNoteInterval);
        }
        this.hideResultModal();
        this.showSection('menu');
    }

    resetGame() {
        if (this.currentGame === 'simon') {
            this.startSimon(this.playerCount);
        } else if (this.currentGame === 'guitar') {
            this.startGuitar(this.playerCount);
        }
    }

    updateModeDisplay() {
        const modeDisplay = document.getElementById('mode-display');
        if (!modeDisplay) return;

        const modes = {
            'simon': 'Memoria',
            'guitar': 'Ritmo',
            'test': 'Configuración'
        };

        modeDisplay.textContent = `Modo: ${modes[this.currentGame] || 'Menú'}`;
    }

    // ===================================================================
    // SIMON DICE
    // ===================================================================

    startSimon(playerCount) {
        console.log(`🧠 Iniciando Simon Dice (${playerCount} jugador${playerCount > 1 ? 'es' : ''})`);
        this.currentGame = 'simon';        this.playerCount = playerCount;        this.resetSimonState();
        this.send({
            type: 'simon_start',
            player_count: playerCount
        });
    }

    resetSimonState() {
        this.simonLevel = 1;
        this.simonCombo = 0;
        this.simonSequence = [];
        document.getElementById('simon-level').textContent = this.simonLevel;
        document.getElementById('simon-combo').textContent = '0';
        document.getElementById('simon-points').textContent = '0';
        document.getElementById('j1-score').textContent = '0';
        document.getElementById('j2-score').textContent = '0';
    }

    handleSimonInput(color, player) {
        if (!this.currentGame === 'simon') return;
        
        this.animateButton(color, player);
        this.send({
            type: 'simon_input',
            player_id: player,
            color: color
        });
    }

    // ===================================================================
    // GUITAR HERO
    // ===================================================================

    startGuitar(playerCount) {
        console.log(`Ritmo - Iniciando (${playerCount} jugador${playerCount > 1 ? 'es' : ''})`);
        this.currentGame = 'guitar';
        this.playerCount = playerCount;
        this.guitarRunning = true;
        this.guitarStartTime = Date.now();
        this.guitarCombo = { 1: 0, 2: 0 };
        this.guitarTimeLeft = 30;
        this.guitarNotes = {};
        
        // Limpiar canvas
        this.drawGuitarStage();

        this.send({
            type: 'guitar_start',
            player_count: playerCount
        });

        // Temporizador de 30 segundos
        this.guitarTimerInterval = setInterval(() => {
            this.guitarTimeLeft--;
            document.getElementById('guitar-time').textContent = this.guitarTimeLeft;
            
            if (this.guitarTimeLeft <= 0) {
                clearInterval(this.guitarTimerInterval);
                this.guitarRunning = false;
                this.showResultScreen();
            }
        }, 1000);

        // Generar notas continuamente cada 0.3 segundos
        this.guitarNoteInterval = setInterval(() => {
            if (this.guitarRunning) {
                for (let p = 1; p <= playerCount; p++) {
                    this.send({
                        type: 'guitar_spawn',
                        player_id: p
                    });
                }
            }
        }, 300);

        // Renderizar loop
        this.guitarRenderLoop();
    }

    drawGuitarStage() {
        const canvas = document.getElementById('guitar-canvas');
        if (!this.canvasContext || !canvas) return;

        const ctx = this.canvasContext;
        const w = canvas.width;
        const h = canvas.height;

        // Fondo
        ctx.fillStyle = '#0d0d0d';
        ctx.fillRect(0, 0, w, h);

        // Línea de impacto (roja)
        ctx.strokeStyle = '#ff4444';
        ctx.lineWidth = 4;
        ctx.beginPath();
        ctx.moveTo(0, this.impactLineY);
        ctx.lineTo(w, this.impactLineY);
        ctx.stroke();

        ctx.fillStyle = '#ff4444';
        ctx.font = 'bold 14px Arial';
        ctx.fillText('IMPACTO', 10, this.impactLineY - 10);

        // Carriles (4 colores)
        const colors = ['#ff6b6b', '#4ecdc4', '#ffe66d', '#95a3ff'];
        const laneWidth = w / 4;

        colors.forEach((color, i) => {
            const x = i * laneWidth;
            ctx.strokeStyle = color;
            ctx.lineWidth = 1;
            ctx.globalAlpha = 0.2;
            ctx.strokeRect(x, 0, laneWidth, h);
            ctx.globalAlpha = 1;
        });

        // Dibujar notas
        for (const noteId in this.guitarNotes) {
            const note = this.guitarNotes[noteId];
            const color = ['#ff6b6b', '#4ecdc4', '#ffe66d', '#95a3ff'][note.color - 1];
            const x = (note.color - 1) * laneWidth + laneWidth / 2 - 30;
            const y = note.y || 0;

            if (y > h) {
                // Nota pasada sin hit
                delete this.guitarNotes[noteId];
                continue;
            }

            ctx.fillStyle = color;
            ctx.globalAlpha = 0.8;
            ctx.fillRect(x, y, 60, this.noteHeight);
            ctx.globalAlpha = 1;
            
            ctx.strokeStyle = color;
            ctx.lineWidth = 2;
            ctx.strokeRect(x, y, 60, this.noteHeight);
        }
    }

    guitarRenderLoop() {
        if (!this.guitarRunning) return;

        const canvas = document.getElementById('guitar-canvas');
        if (!canvas) return;

        // Actualizar posiciones de notas
        for (const noteId in this.guitarNotes) {
            const note = this.guitarNotes[noteId];
            const elapsed = (Date.now() - note.spawnTime) / 1000;
            const speed = 150; // píxeles por segundo
            note.y = (elapsed * speed);
        }

        this.drawGuitarStage();
        requestAnimationFrame(() => this.guitarRenderLoop());
    }

    // ===================================================================
    // MANEJO DE INPUTS
    // ===================================================================

    handleButtonPress(color, player) {
        if (!this.currentGame) return;

        if (this.currentGame === 'simon') {
            this.handleSimonInput(color, player);
        } else if (this.currentGame === 'guitar') {
            this.handleGuitarInput(color, player);
        }
    }

    handleGuitarInput(color, player) {
        if (!this.guitarRunning) return;

        this.animateButton(color, player);

        // Calcular accuracy basado en la nota más cercana
        let bestAccuracy = 0;
        let targetNoteId = null;

        for (const noteId in this.guitarNotes) {
            const note = this.guitarNotes[noteId];
            if (note.color === color && note.player === player) {
                const distFromImpact = Math.abs(note.y - this.impactLineY);
                const maxDistance = 80;
                const accuracy = Math.max(0, 1 - (distFromImpact / maxDistance));

                if (accuracy > bestAccuracy) {
                    bestAccuracy = accuracy;
                    targetNoteId = noteId;
                }
            }
        }

        if (targetNoteId) {
            delete this.guitarNotes[targetNoteId];
        }

        this.send({
            type: 'guitar_input',
            player_id: player,
            color: color,
            accuracy: bestAccuracy
        });
    }

    animateButton(color, player) {
        const buttons = document.querySelectorAll(`.btn[data-color="${color}"]`);
        buttons.forEach(btn => {
            if (!btn.dataset.player || parseInt(btn.dataset.player) === player) {
                btn.style.transform = 'scale(0.9)';
                setTimeout(() => {
                    btn.style.transform = '';
                }, 100);
            }
        });
    }

    // ===================================================================
    // HARDWARE TEST
    // ===================================================================

    testLED(ledNum) {
        console.log(`🔧 Test LED ${ledNum}`);
        this.send({
            type: 'led_test',
            led_num: ledNum
        });
    }

    testLCD() {
        const line1 = document.getElementById('lcd-line1')?.value || '';
        const line2 = document.getElementById('lcd-line2')?.value || '';

        console.log(`🔧 Test LCD: "${line1}" / "${line2}"`);
        this.send({
            type: 'lcd_write',
            line1: line1,
            line2: line2
        });
    }

    // ===================================================================
    // MANEJO DE MENSAJES
    // ===================================================================

    handleMessage(data) {
        const type = data.type;

        if (type === 'init') {
            this.simulationMode = data.simulation_mode;
            if (this.simulationMode) {
                this.showToast('⚠️ Modo simulación (PC fallback)', 'success');
            }
        }

        // Simon Dice feedback
        if (type === 'simon_feedback') {
            this.updateSimonUI(data);
        }

        // Guitar Hero feedback
        if (type === 'guitar_feedback') {
            this.updateGuitarUI(data);
        }

        // Notas de Guitar Hero
        if (type === 'guitar_spawn') {
            const note = data.note;
            this.guitarNotes[note.note_id] = {
                color: note.color,
                spawnTime: note.spawn_time * 1000,
                y: 0,
                player: 1
            };
        }

        if (type === 'guitar_feedback') {
            this.updateGuitarUI(data);
        }
    }

    updateSimonUI(data) {
        const score = data.score || 0;
        const combo = data.combo || 0;
        const correct = data.correct;
        const message = data.message || '';

        document.getElementById('j1-score').textContent = score;
        document.getElementById('j1-combo').textContent = combo;
        document.getElementById('simon-points').textContent = score;

        const statusEl = document.getElementById('simon-status');
        if (statusEl) {
            statusEl.textContent = message;
            statusEl.style.color = correct ? '#7B2CBF' : '#ff4444';
        }
        // Sin toast - el contador es suficiente
    }

    updateGuitarUI(data) {
        const result = data.result;
        const points = data.points;
        const combo = data.combo;
        const playerId = data.player_id || 1;
        const scores = data.scores || {};

        // Actualizar scores en this.players para que se usen en showGuitarResult()
        if (scores[1] !== undefined) {
            this.players[1].score = scores[1];
        }
        if (scores[2] !== undefined) {
            this.players[2].score = scores[2];
        }

        // Actualizar UI del jugador que hizo el input
        if (playerId === 1) {
            document.getElementById('g-j1-score').textContent = scores[1] || 0;
        } else if (playerId === 2) {
            document.getElementById('g-j2-score').textContent = scores[2] || 0;
        }

        // Actualizar combo
        document.getElementById('g-j1-combo').textContent = combo;
        if (this.playerCount === 2) {
            document.getElementById('g-j2-combo').textContent = this.guitarCombo[2] || 0;
        }
        // Sin toast - el contador es suficiente
    }

    // ===================================================================
    // RESULT SCREEN
    // ===================================================================

    showResultScreen() {
        if (this.currentGame === 'simon') {
            this.showSimonResult();
        } else if (this.currentGame === 'guitar') {
            this.showGuitarResult();
        }
    }

    showSimonResult() {
        const modal = document.getElementById('result-modal');
        const title = document.getElementById('result-title');
        const body = document.getElementById('result-body');

        title.textContent = 'Memoria - Juego Terminado';

        if (this.playerCount === 1) {
            body.innerHTML = `
                <div class="score">Puntuación Final</div>
                <div class="winner">${this.players[1]?.score || 0} Puntos</div>
                <div class="score">Nivel Alcanzado: ${this.simonLevel}</div>
                <div class="score">Rachas: ${this.players[1]?.combo || 0}</div>
            `;
        } else {
            const p1Score = this.players[1]?.score || 0;
            const p2Score = this.players[2]?.score || 0;
            const winner = p1Score > p2Score ? 'Jugador 1' : p2Score > p1Score ? 'Jugador 2' : 'Empate';

            body.innerHTML = `
                <div class="winner">${winner}</div>
                <div style="margin-top: 20px;">
                    <div class="score">Jugador 1: ${p1Score} pts</div>
                    <div class="score">Jugador 2: ${p2Score} pts</div>
                </div>
            `;
        }

        modal.classList.remove('hidden');
    }

    showGuitarResult() {
        const modal = document.getElementById('result-modal');
        const title = document.getElementById('result-title');
        const body = document.getElementById('result-body');

        title.textContent = 'Ritmo - Juego Terminado';

        if (this.playerCount === 1) {
            body.innerHTML = `
                <div class="score">Puntuación Final</div>
                <div class="winner">${this.players[1]?.score || 0} Puntos</div>
                <div class="score">Racha Máxima: ${this.guitarCombo[1]} Notas</div>
            `;
        } else {
            const p1Score = this.players[1]?.score || 0;
            const p2Score = this.players[2]?.score || 0;
            const winner = p1Score > p2Score ? 'Jugador 1' : p2Score > p1Score ? 'Jugador 2' : 'Empate';

            body.innerHTML = `
                <div class="winner">${winner}</div>
                <div style="margin-top: 20px;">
                    <div class="score">Jugador 1: ${p1Score} pts (Racha: ${this.guitarCombo[1]})</div>
                    <div class="score">Jugador 2: ${p2Score} pts (Racha: ${this.guitarCombo[2]})</div>
                </div>
            `;
        }

        modal.classList.remove('hidden');
    }

    hideResultModal() {
        const modal = document.getElementById('result-modal');
        modal.classList.add('hidden');
    }

    setConnectionStatus(connected) {
        this.connected = connected;
        const dot = document.getElementById('connection-status');
        if (dot) {
            if (connected) {
                dot.classList.add('connected');
            } else {
                dot.classList.remove('connected');
            }
        }
    }

    showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;

        container.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    send(data) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        } else {
            console.warn('WebSocket no está conectado');
        }
    }
}

// ===================================================================
// INICIALIZAR APLICACIÓN
// ===================================================================

let game;

document.addEventListener('DOMContentLoaded', () => {
    game = new XboxArcadeGame();
});
