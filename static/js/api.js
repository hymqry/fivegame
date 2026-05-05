const API_BASE = window.location.origin;

async function apiRequest(method, path, body) {
    const options = {
        method: method,
        headers: { 'Content-Type': 'application/json' },
    };
    if (body) {
        options.body = JSON.stringify(body);
    }
    const resp = await fetch(API_BASE + path, options);
    return resp.json();
}

function newGame(mode) {
    return apiRequest('POST', '/api/game/new', { mode: mode });
}

function makeMove(row, col) {
    return apiRequest('POST', '/api/game/move', { row: row, col: col });
}

function getGameState() {
    return apiRequest('GET', '/api/game/state');
}
