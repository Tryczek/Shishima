const apiUrl = 'http://127.0.0.1:5000';
let gameId = null;
let currentPlayer = 'Player1';
let setupPhase = true;
let selectedFromPosition = null;
let gameMode = null;
let aiPlayer = null;
let gameEnded = false;

document.getElementById('human-vs-human').addEventListener('click', () => {
    gameMode = 'human-vs-human';
    aiPlayer = null;
    startGame();
});

document.getElementById('human-vs-ai').addEventListener('click', () => {
    gameMode = 'human-vs-ai';
    aiPlayer = 'Player2';
    startGame();
});

document.getElementById('reset-game').addEventListener('click', resetGame);
document.getElementById('load-from-file').addEventListener('click', loadFromFile);
document.getElementById('load-from-memory').addEventListener('click', loadFromMemory);
document.getElementById('save-game').addEventListener('click', saveGame);

async function startGame() {
    const response = await fetch(`${apiUrl}/init`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            player1: 'Player1',
            player2: 'Player2'
        })
    });
    const data = await response.json();
    gameId = data.game_id;
    currentPlayer = 'Player1';
    setupPhase = true;
    selectedFromPosition = null;
    gameEnded = false;
    document.getElementById('game-mode').style.display = 'none';
    document.getElementById('game').style.display = 'block';
    initializeBoard();
    updateCurrentPlayerText();
}

function initializeBoard() {
    const board = document.getElementById('board');
    board.innerHTML = '';
    const positions = [
        "0,0", "0,1", "0,2",
        "1,0", "1,1", "1,2",
        "2,0", "2,1", "2,2"
    ];
    positions.forEach(pos => {
        const [i, j] = pos.split(',').map(Number);
        const cell = document.createElement('div');
        cell.classList.add('cell');
        cell.dataset.position = `${i},${j}`;
        cell.addEventListener('click', () => makeMove(cell));
        board.appendChild(cell);
    });
    updateDebugBoard();
}

async function makeMove(cell) {
    if (currentPlayer === aiPlayer || gameEnded) {
        return; // Ignorujemy kliknięcia, gdy gra się skończyła lub jest ruch AI
    }

    const [row, col] = cell.dataset.position.split(',').map(Number);
    if (setupPhase) {
        const response = await fetch(`${apiUrl}/move`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                game_id: gameId,
                player: currentPlayer,
                from: null,
                to: [row, col]
            })
        });
        const data = await response.json();
        if (data.error) {
            showMessage(data.error);
            return;
        }
        updateBoard(data.board);
        if (!data.setup_phase) {
            setupPhase = false;
        }
        currentPlayer = data.current_player;
        updateCurrentPlayerText();
        if (currentPlayer === aiPlayer) {
            makeAiSetupMove();
        }
    } else {
        const cellPosition = [row, col];
        if (selectedFromPosition && selectedFromPosition[0] === row && selectedFromPosition[1] === col) {
            selectedFromPosition = null;
            cell.classList.remove('selected');
        } else if (selectedFromPosition === null) {
            selectedFromPosition = cellPosition;
            cell.classList.add('selected');
        } else {
            const response = await fetch(`${apiUrl}/move`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    game_id: gameId,
                    player: currentPlayer,
                    from: selectedFromPosition,
                    to: [row, col]
                })
            });
            const data = await response.json();
            if (data.error) {
                showMessage(data.error);
                return;
            }
            updateBoard(data.board);
            selectedFromPosition = null;
            document.querySelectorAll('.cell').forEach(cell => cell.classList.remove('selected'));

            if (data.winner) {
                setTimeout(() => {
                    showMessageWinner(`Player ${data.winner} wins!`, data.winner);
                    gameEnded = true;
                }, 100);
            } else {
                currentPlayer = data.current_player;
                updateCurrentPlayerText();
                if (currentPlayer === aiPlayer) {
                    makeAiMove();
                }
            }
        }
    }
    updateDebugBoard();
}

async function makeAiSetupMove() {
    const response = await fetch(`${apiUrl}/ai_setup_move`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            game_id: gameId,
            player: aiPlayer
        })
    });
    const data = await response.json();
    updateBoard(data.board);
    if (!data.setup_phase) {
        setupPhase = false;
    }
    currentPlayer = data.current_player;
    updateCurrentPlayerText();
    if (currentPlayer === aiPlayer && setupPhase) {
        makeAiSetupMove(); // Kontynuuj ustawianie pionków dla AI
    } else if (currentPlayer === aiPlayer) {
        makeAiMove(); // Przejdź do fazy ruchów AI
    }
    updateDebugBoard();
}

async function makeAiMove() {
    const response = await fetch(`${apiUrl}/ai_move`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            game_id: gameId,
            player: aiPlayer
        })
    });
    const data = await response.json();
    updateBoard(data.board);
    if (data.winner) {
        setTimeout(() => {
            showMessageWinner(`Player ${data.winner} wins!`, data.winner);
            gameEnded = true;
        }, 100);
    } else {
        currentPlayer = data.current_player;
        updateCurrentPlayerText();
    }
    updateDebugBoard();
}

async function resetGame() {
    const response = await fetch(`${apiUrl}/end/${gameId}`, {
        method: 'POST'
    });
    document.getElementById('game').style.display = 'none';
    document.getElementById('game-mode').style.display = 'block';
    document.getElementById('board').innerHTML = '';
    document.getElementById('debug-board').textContent = '';
    document.getElementById('current-player').textContent = '';
    document.getElementById('message').textContent = '';
    gameEnded = false;
}

async function loadFromFile() {
    const response = await fetch(`${apiUrl}/load/file`, {
        method: 'GET'
    });
    const data = await response.json();
    if (data.error) {
        showMessage(data.error);
        return;
    }
    loadGame(data);
}

async function loadFromMemory() {
    const response = await fetch(`${apiUrl}/load/memory`, {
        method: 'GET'
    });
    const data = await response.json();
    if (data.error) {
        showMessage(data.error);
        return;
    }
    loadGame(data);
}

function loadGame(data) {
    gameId = data.game_id;
    currentPlayer = data.current_player;
    setupPhase = data.setup_phase;
    updateBoard(data.board);
    updateCurrentPlayerText();
    document.getElementById('game-mode').style.display = 'none';
    document.getElementById('game').style.display = 'block';
    updateDebugBoard();
}

async function saveGame() {
    const response = await fetch(`${apiUrl}/save`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            game_id: gameId
        })
    });
    const data = await response.json();
    if (data.error) {
        showMessage(data.error);
        return;
    }
    showMessage('Game saved successfully!');
}

function updateBoard(board) {
    const cells = document.querySelectorAll('.cell');
    cells.forEach(cell => {
        const [row, col] = cell.dataset.position.split(',').map(Number);
        cell.classList.remove('occupied-player1', 'occupied-player2', 'selected');
        if (board[row][col] === 'Player1') {
            cell.classList.add('occupied-player1');
        } else if (board[row][col] === 'Player2') {
            cell.classList.add('occupied-player2');
        }
    });
}

function updateCurrentPlayerText() {
    const currentPlayerText = document.getElementById('current-player');
    const playerText = currentPlayer === 'Player1' ? '<span class="red-player">RED</span>' : '<span class="blue-player">BLUE</span>';
    currentPlayerText.innerHTML = `${playerText} Player Moves`;
}

function updateDebugBoard() {
    const board = document.getElementById('board');
    const debugBoard = document.getElementById('debug-board');
    const rows = [];
    for (let i = 0; i < 3; i++) {
        const row = [];
        for (let j = 0; j < 3; j++) {
            const cell = board.querySelector(`.cell[data-position='${i},${j}']`);
            const isPlayer1 = cell.classList.contains('occupied-player1');
            const isPlayer2 = cell.classList.contains('occupied-player2');
            if (isPlayer1) {
                row.push('1');
            } else if (isPlayer2) {
                row.push('2');
            } else {
                row.push('0');
            }
        }
        rows.push(row.join(''));
    }
    debugBoard.textContent = rows.join(',');
}

function showMessage(message) {
    const messageElement = document.getElementById('message');
    messageElement.textContent = message;
    messageElement.style.display = 'block';
}

function showMessageWinner(message, winner) {
    const messageElement = document.getElementById('message');
    const winnerText = winner === 'Player1' ? '<strong style="color: red;">RED</strong>' : '<strong style="color: blue;">BLUE</strong>';
    messageElement.innerHTML = `${winnerText} Player wins!`;
    messageElement.style.display = 'block';
}
