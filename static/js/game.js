const BOARD_SIZE = 15;
const CELL_SIZE = 600 / BOARD_SIZE;
const EMPTY = 0, BLACK = 1, WHITE = 2;
const PLAYER_NAMES = { 1: '黑棋(X)', 2: '白棋(O)' };

let canvas, ctx;
let gameMode = 'pvp';
let board = [];
let currentPlayer = BLACK;
let gameOver = false;
let isAIThinking = false;
let lastAIMove = null;

function initCanvas() {
    canvas = document.getElementById('board');
    ctx = canvas.getContext('2d');
    canvas.addEventListener('click', onCanvasClick);
    drawBoard();
}

function drawBoard() {
    ctx.clearRect(0, 0, 600, 600);

    // Background
    ctx.fillStyle = '#deb887';
    ctx.fillRect(0, 0, 600, 600);

    // Grid lines
    ctx.strokeStyle = '#333';
    ctx.lineWidth = 1;
    for (let i = 0; i < BOARD_SIZE; i++) {
        const pos = i * CELL_SIZE + CELL_SIZE / 2;
        ctx.beginPath();
        ctx.moveTo(CELL_SIZE / 2, pos);
        ctx.lineTo(600 - CELL_SIZE / 2, pos);
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(pos, CELL_SIZE / 2);
        ctx.lineTo(pos, 600 - CELL_SIZE / 2);
        ctx.stroke();
    }

    // Star points (天元和星位)
    const starPoints = [
        [3, 3], [3, 7], [3, 11],
        [7, 3], [7, 7], [7, 11],
        [11, 3], [11, 7], [11, 11]
    ];
    ctx.fillStyle = '#333';
    for (const [r, c] of starPoints) {
        const x = c * CELL_SIZE + CELL_SIZE / 2;
        const y = r * CELL_SIZE + CELL_SIZE / 2;
        ctx.beginPath();
        ctx.arc(x, y, 4, 0, Math.PI * 2);
        ctx.fill();
    }

    // Stones
    for (let r = 0; r < BOARD_SIZE; r++) {
        for (let c = 0; c < BOARD_SIZE; c++) {
            if (board[r] && board[r][c] !== EMPTY) {
                drawStone(r, c, board[r][c]);
            }
        }
    }

    // Highlight last AI move
    if (lastAIMove) {
        const x = lastAIMove.col * CELL_SIZE + CELL_SIZE / 2;
        const y = lastAIMove.row * CELL_SIZE + CELL_SIZE / 2;
        ctx.strokeStyle = '#ff0000';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(x, y, CELL_SIZE / 2 - 3, 0, Math.PI * 2);
        ctx.stroke();
    }
}

function drawStone(row, col, player) {
    const x = col * CELL_SIZE + CELL_SIZE / 2;
    const y = row * CELL_SIZE + CELL_SIZE / 2;
    const radius = CELL_SIZE / 2 - 4;

    ctx.beginPath();
    ctx.arc(x, y, radius, 0, Math.PI * 2);

    if (player === BLACK) {
        const grad = ctx.createRadialGradient(x - 4, y - 4, 2, x, y, radius);
        grad.addColorStop(0, '#555');
        grad.addColorStop(1, '#000');
        ctx.fillStyle = grad;
    } else {
        const grad = ctx.createRadialGradient(x - 4, y - 4, 2, x, y, radius);
        grad.addColorStop(0, '#fff');
        grad.addColorStop(1, '#ccc');
        ctx.fillStyle = grad;
    }
    ctx.fill();
    ctx.strokeStyle = player === BLACK ? '#000' : '#999';
    ctx.lineWidth = 1;
    ctx.stroke();
}

function onCanvasClick(e) {
    if (gameOver || isAIThinking) return;
    if (gameMode === 'pve' && currentPlayer !== BLACK) return;

    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    const x = (e.clientX - rect.left) * scaleX;
    const y = (e.clientY - rect.top) * scaleY;

    const col = Math.floor(x / CELL_SIZE);
    const row = Math.floor(y / CELL_SIZE);

    if (row < 0 || row >= BOARD_SIZE || col < 0 || col >= BOARD_SIZE) return;
    if (board[row][col] !== EMPTY) return;

    placeStone(row, col);
}

async function placeStone(row, col) {
    try {
        const result = await makeMove(row, col);
        if (!result.success) return;

        // Refresh full board state
        await refreshState();

        // If PvE mode and AI moved, mark AI move
        if (result.aiRow >= 0) {
            lastAIMove = { row: result.aiRow, col: result.aiCol };
        } else {
            lastAIMove = null;
        }

        drawBoard();
        updateStatus();

        if (result.gameOver) {
            gameOver = true;
            showResult(result.winner);
        } else if (gameMode === 'pve' && currentPlayer === WHITE) {
            // AI's turn - already handled by the server
        }
    } catch (err) {
        console.error('Move failed:', err);
    }
}

async function refreshState() {
    const state = await getGameState();
    board = state.board;
    currentPlayer = state.currentPlayer;
    gameOver = state.gameOver;
}

function updateStatus() {
    const statusEl = document.getElementById('status-text');
    if (gameOver) {
        statusEl.textContent = '游戏结束';
    } else {
        statusEl.textContent = `${PLAYER_NAMES[currentPlayer]} 回合`;
    }
}

function showResult(winner) {
    const modal = document.getElementById('result-modal');
    const text = document.getElementById('result-text');
    if (winner === EMPTY) {
        text.textContent = '平局！';
    } else {
        text.textContent = `${PLAYER_NAMES[winner]} 获胜！`;
    }
    modal.style.display = 'flex';
}

function showMenu() {
    document.getElementById('result-modal').style.display = 'none';
    document.getElementById('game-area').style.display = 'none';
    document.getElementById('menu').style.display = 'block';
}

async function startGame(mode) {
    gameMode = mode;
    lastAIMove = null;
    isAIThinking = false;

    document.getElementById('menu').style.display = 'none';
    document.getElementById('game-area').style.display = 'inline-block';

    if (!canvas) {
        initCanvas();
    }

    try {
        await newGame(mode);
        await refreshState();
        drawBoard();
        updateStatus();
    } catch (err) {
        console.error('Failed to start game:', err);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    initCanvas();
});
