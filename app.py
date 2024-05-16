from flask import Flask, request, jsonify, render_template
from game_engine import ShishimaGame
from storage import InMemoryStorage, FileStorage
import json

app = Flask(__name__)

# Load configuration
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

# Choose storage method
if config['storage'] == 'memory':
    storage = InMemoryStorage()
else:
    storage = FileStorage(config['file_path'])

games = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/init', methods=['POST'])
def init_game():
    player1 = request.json['player1']
    player2 = request.json['player2']
    game_id = storage.create_game(player1, player2)
    games[game_id] = ShishimaGame(player1, player2)
    return jsonify({"game_id": game_id, "status": "Game initialized"})

@app.route('/move', methods=['POST'])
def make_move():
    game_id = request.json['game_id']
    player = request.json['player']
    from_position = request.json.get('from')
    to_position = request.json['to']
    
    game = games.get(game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404
    
    move_result = game.move(player, from_position, to_position)
    storage.save_game(game_id, game)
    return jsonify(move_result)

@app.route('/ai_setup_move', methods=['POST'])
def ai_setup_move():
    game_id = request.json['game_id']
    player = request.json['player']
    
    game = games.get(game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404

    move_result = game.random_setup_move(player)
    storage.save_game(game_id, game)
    return jsonify(move_result)

@app.route('/ai_move', methods=['POST'])
def ai_move():
    game_id = request.json['game_id']
    player = request.json['player']
    
    game = games.get(game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404

    move_result = game.random_move(player)
    storage.save_game(game_id, game)
    return jsonify(move_result)

@app.route('/load/file', methods=['GET'])
def load_from_file():
    data = storage.load_from_file()
    if not data:
        return jsonify({"error": "No game saved in file"}), 404
    
    game_id = data['game_id']
    games[game_id] = ShishimaGame(data['player1'], data['player2'])
    games[game_id].board = data['board']
    games[game_id].current_player = data['current_player']
    games[game_id].setup_phase = data['setup_phase']
    games[game_id].player_positions = data['player_positions']
    games[game_id].setup_completed = data['setup_completed']
    return jsonify(data)

@app.route('/load/memory', methods=['GET'])
def load_from_memory():
    data = storage.load_from_memory()
    if not data:
        return jsonify({"error": "No game saved in memory"}), 404
    
    game_id = data['game_id']
    games[game_id] = ShishimaGame(data['player1'], data['player2'])
    games[game_id].board = data['board']
    games[game_id].current_player = data['current_player']
    games[game_id].setup_phase = data['setup_phase']
    games[game_id].player_positions = data['player_positions']
    games[game_id].setup_completed = data['setup_completed']
    return jsonify(data)

@app.route('/save', methods=['POST'])
def save_game():
    game_id = request.json['game_id']
    game = games.get(game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404
    
    storage.save_game(game_id, game)
    storage.save_to_file(game_id, game)
    return jsonify({"status": "Game saved successfully"})

@app.route('/status/<game_id>', methods=['GET'])
def game_status(game_id):
    game = games.get(game_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404
    return jsonify(game.status())

@app.route('/end/<game_id>', methods=['POST'])
def end_game(game_id):
    if game_id in games:
        del games[game_id]
        storage.delete_game(game_id)
        return jsonify({"status": "Game ended"})
    return jsonify({"error": "Game not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
