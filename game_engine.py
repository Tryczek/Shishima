import random

class ShishimaGame:
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.board = [[None for _ in range(3)] for _ in range(3)]
        self.current_player = player1
        self.move_count = 0
        self.setup_phase = True
        self.player_positions = {player1: [], player2: []}
        self.setup_completed = {player1: False, player2: False}
        self.center_position = (1, 1)

    def move(self, player, from_position, to_position):
        if self.setup_phase:
            return self.setup_move(player, to_position)
        else:
            return self.normal_move(player, from_position, to_position)

    def setup_move(self, player, to_position):
        if self.setup_completed[player]:
            return {"error": "Setup already completed for this player"}

        if len(self.player_positions[player]) >= 3:
            self.setup_completed[player] = True
            if self.setup_completed[self.player1] and self.setup_completed[self.player2]:
                self.setup_phase = False
            self.switch_player()
            return {"status": "Setup phase completed for this player"}

        if not self.is_valid_position(to_position):
            return {"error": "Invalid position"}

        if self.board[to_position[0]][to_position[1]] is not None:
            return {"error": "Position already taken"}
        print(to_position)

        # Rule 1: Cannot place a piece in the center during setup phase
        if to_position == [1,1]:
            return {"error": "Cannot place a piece in the center during setup phase"}

        # Rule 2: From the second placement, must place next to another piece of the same player
        if len(self.player_positions[player]) > 0 and not self.is_adjacent_to_own_piece(player, to_position):
            return {"error": "Must place next to another piece of the same player"}

        self.board[to_position[0]][to_position[1]] = player
        self.player_positions[player].append(to_position)

        if len(self.player_positions[player]) == 3:
            self.setup_completed[player] = True
            if self.setup_completed[self.player1] and self.setup_completed[self.player2]:
                self.setup_phase = False

        self.switch_player()
        return {"status": "Piece placed", "board": self.board, "current_player": self.current_player, "setup_phase": self.setup_phase}

    def random_setup_move(self, player):
        valid_positions = [(i, j) for i in range(3) for j in range(3) if self.board[i][j] is None and (i, j) != self.center_position]
        if len(self.player_positions[player]) > 0:
            valid_positions = [pos for pos in valid_positions if self.is_adjacent_to_own_piece(player, pos)]
        if valid_positions:
            to_position = random.choice(valid_positions)
            self.setup_move(player, to_position)
        return {"status": "Piece placed", "board": self.board, "current_player": self.current_player, "setup_phase": self.setup_phase}

    def normal_move(self, player, from_position, to_position):
        if self.current_player != player:
            return {"error": "Not your turn"}

        if not self.is_valid_position(from_position) or not self.is_valid_position(to_position):
            return {"error": "Invalid position"}

        if self.board[from_position[0]][from_position[1]] != player:
            return {"error": "Choose your own piece to move"}

        if self.board[to_position[0]][to_position[1]] is not None:
            return {"error": "Position already taken"}

        if not self.is_adjacent(from_position, to_position):
            return {"error": "Invalid move"}

        self.board[from_position[0]][from_position[1]] = None
        self.board[to_position[0]][to_position[1]] = player

        self.update_player_positions(player, from_position, to_position)
        
        if self.check_winner(player):
            return {"status": f"Player {player} wins!", "board": self.board, "winner": player}

        self.switch_player()
        return {"status": "Move made", "board": self.board, "current_player": self.current_player, "setup_phase": self.setup_phase}

    def random_move(self, player):
        valid_moves = self.get_valid_moves(player)
        if not valid_moves:
            return {"error": "No valid moves available"}
        from_position, to_position = random.choice(valid_moves)
        return self.normal_move(player, from_position, to_position)

    def get_valid_moves(self, player):
        valid_moves = []
        for from_position in self.player_positions[player]:
            for to_position in [(i, j) for i in range(3) for j in range(3)]:
                if self.board[to_position[0]][to_position[1]] is None and self.is_adjacent(from_position, to_position):
                    valid_moves.append((from_position, to_position))
        return valid_moves

    def is_valid_position(self, position):
        return 0 <= position[0] < 3 and 0 <= position[1] < 3

    def is_adjacent(self, from_position, to_position):
        dx = abs(from_position[0] - to_position[0])
        dy = abs(from_position[1] - to_position[1])

        if from_position == [1, 1] or to_position == [1, 1]:
            return True  # Ze środka lub do środka można się ruszać w każdą stronę

        if (dx == 1 and dy == 0) or (dx == 0 and dy == 1):
            return True

        return False

    def is_adjacent_to_own_piece(self, player, position):
        for pos in self.player_positions[player]:
            if self.is_adjacent(pos, position):
                return True
        return False

    def update_player_positions(self, player, from_position, to_position):
        self.player_positions[player].remove(from_position)
        self.player_positions[player].append(to_position)

    def check_winner(self, player):
        middle = (1, 1)
        if self.board[middle[0]][middle[1]] != player:
            return False

        lines = [
            [(0, 0), (2, 2)], # Diagonal \
            [(0, 2), (2, 0)], # Diagonal /
            [(0, 1), (2, 1)], # Vertical |
            [(1, 0), (1, 2)]  # Horizontal -
        ]

        for line in lines:
            if all(self.board[pos[0]][pos[1]] == player for pos in line):
                return True

        return False

    def switch_player(self):
        self.current_player = self.player2 if self.current_player == self.player1 else self.player1

    def status(self):
        return {
            "game_id": self.player1,  # or self.player2, assuming player1 or player2 is unique enough
            "player1": self.player1,
            "player2": self.player2,
            "board": self.board,
            "current_player": self.current_player,
            "setup_phase": self.setup_phase,
            "player_positions": self.player_positions,
            "setup_completed": self.setup_completed
        }
