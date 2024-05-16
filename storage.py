import json
import os

class InMemoryStorage:
    def __init__(self):
        self.games = {}
        self.last_saved_game = None
    
    def create_game(self, player1, player2):
        game_id = str(len(self.games) + 1)
        self.games[game_id] = {"player1": player1, "player2": player2, "board": None}
        return game_id
    
    def save_game(self, game_id, game):
        self.games[game_id] = game.status()
        self.last_saved_game = self.games[game_id]
    
    def load_from_memory(self):
        if not self.last_saved_game:
            return None
        return self.last_saved_game

    def save_to_file(self, game_id, game):
        with open('saved_game.json', 'w') as file:
            json.dump(game.status(), file)
    
    def load_from_file(self):
        if not os.path.exists('saved_game.json'):
            return None
        with open('saved_game.json', 'r') as file:
            return json.load(file)

    def delete_game(self, game_id):
        if game_id in self.games:
            del self.games[game_id]

class FileStorage:
    def __init__(self, file_path):
        self.file_path = file_path
        if not os.path.exists(file_path):
            with open(file_path, 'w') as file:
                json.dump({}, file)
    
    def _load_data(self):
        with open(self.file_path, 'r') as file:
            return json.load(file)
    
    def _save_data(self, data):
        with open(self.file_path, 'w') as file:
            json.dump(data, file)
    
    def create_game(self, player1, player2):
        data = self._load_data()
        game_id = str(len(data) + 1)
        data[game_id] = {"player1": player1, "player2": player2, "board": None}
        self._save_data(data)
        return game_id
    
    def save_game(self, game_id, game):
        data = self._load_data()
        data[game_id] = game.status()
        self._save_data(data)
    
    def save_to_file(self, game_id, game):
        self.save_game(game_id, game)

    def load_from_file(self):
        data = self._load_data()
        if not data:
            return None
        game_id = max(data.keys())
        return data[game_id]

    def load_from_memory(self):
        return self.load_from_file()

    def delete_game(self, game_id):
        data = self._load_data()
        if game_id in data:
            del data[game_id]
            self._save_data(data)
