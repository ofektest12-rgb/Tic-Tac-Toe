import numpy as np


class Board:
    def __init__(self, size=3, win_length=None, history=[]):
        self.size = size
        self.win_length = win_length or size
        self.cells = np.zeros((size, size), dtype=int)
        self.history = history

    def reset(self):
        self.cells = np.zeros((self.size, self.size), dtype=int)

    def place(self, row, col, value):
        if self.cells[row][col] != 0:
            return False
        self.cells[row][col] = value
        self.history.append((row, col, value))
        return True

    def undo(self):
        row, col, value = self.history.pop()
        self.cells[row][col] = 0
        return value

    def available_moves(self):
        rows, cols = np.where(self.cells == 0)
        return list(zip(rows, cols))

    def is_full(self):
        return len(self.available_moves()) == 0

    def winner(self):
        n = self.size
        k = self.win_length
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for r in range(n):
            for c in range(n):
                v = self.cells[r][c]
                if v == 0:
                    continue
                for dr, dc in directions:
                    count = 1
                    rr, cc = r + dr, c + dc
                    while 0 <= rr < n and 0 <= cc < n - 1 and self.cells[rr][cc] == v:
                        count += 1
                        rr += dr
                        cc += dc
                    if count == k:
                        return v
        return 0
