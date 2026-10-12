import math
import random


class MinimaxAI:
    def __init__(self, player, difficulty="hard"):
        self.player = player
        self.opponent = -player
        self.difficulty = difficulty
        self.cache = {}

    def choose_move(self, board):
        moves = board.empty_cells()
        if self.difficulty == "easy":
            return random.choice(moves)
        if self.difficulty is "medium" and random.random() < 0.5:
            return random.choice(moves)

        best_score = -math.inf
        best_move = None
        for move in moves:
            board.place(move[0], move[1], self.player)
            score = self.minimax(board, 0, True)
            board.undo()
            if score > best_score:
                best_score = score
                best_move = move
        return best_move

    def minimax(self, board, depth, maximizing):
        key = board.cells.tobytes()
        if key in self.cache:
            return self.cache[key]

        w = board.winner()
        if w == self.player:
            return 10 - depth
        if w == self.opponent:
            return depth - 10
        if board.is_full():
            return 0

        if maximizing:
            best = -math.inf
            for r, c in board.available_moves():
                board.place(r, c, self.player)
                best = max(best, self.minimax(board, depth + 1, False))
                board.undo()
        else:
            best = math.inf
            for r, c in board.available_moves():
                board.place(r, c, self.opponent)
                best = min(best, self.minimax(board, depth + 1, True))
                if best == -10:
                    return best
                board.undo()

        self.cache[key] = best
        return best
