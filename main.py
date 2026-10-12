# Author: aqeelanwar
# Created: 12 March,2020, 7:06 PM
# Email: aqeel.anwar@gatech.edu

import os
import sys
import threading
import time
from tkinter import *
from tkinter import simpledialog

import numpy as np

import storage
from ai import MinimaxAI
from board import Board

size_of_board = 600
symbol_thickness = 50
symbol_X_color = '#EE4035'
symbol_O_color = '#0492CF'
Green_color = '#7BC043'


class Tic_Tac_Toe():
    def __init__(self, n=3, vs_ai=False, difficulty="hard"):
        self.window = Tk()
        self.window.title('Tic-Tac-Toe')
        self.canvas = Canvas(self.window, width=size_of_board, height=size_of_board)
        self.canvas.pack()
        self.window.bind('<Button-1>', self.click)
        self.window.bind('<Control-z>', self.undo)
        self.window.bind('<Control-s>', self.save_session)
        self.window.bind('<Control-o>', self.load_session)

        self.n = n
        self.cell_size = size_of_board / n
        self.symbol_size = (self.cell_size - size_of_board / 8) / 2
        self.board = Board(size=n)
        self.vs_ai = vs_ai
        self.ai = MinimaxAI(player=1, difficulty=difficulty) if vs_ai else None

        self.player_X_name = simpledialog.askstring("Player 1", "Name for X:") or "Player 1"
        if vs_ai:
            self.player_O_name = "Computer"
        else:
            self.player_O_name = simpledialog.askstring("Player 2", "Name for O:") or "Player 2"

        self.initialize_board()
        self.player_X_turns = True
        self.player_X_starts = True
        self.reset_board = False
        self.gameover = False
        self.tie = False
        self.X_wins = False
        self.O_wins = False

        scores = storage.load_scores()
        self.X_score = scores["X"]
        self.O_score = scores["O"]
        self.tie_score = scores["tie"]

        self.db = storage.init_db()
        self.elapsed = 0
        self.timer_running = True
        threading.Thread(target=self.run_timer, daemon=True).start()

    def mainloop(self):
        self.window.mainloop()

    def run_timer(self):
        while self.timer_running:
            time.sleep(1)
            self.elapsed += 1
            self.canvas.delete("timer")
            self.canvas.create_text(size_of_board - 40, 15, text=f"{self.elapsed}s", tags="timer", fill="gray")

    def initialize_board(self):
        for i in range(self.n - 1):
            self.canvas.create_line((i + 1) * self.cell_size, 0, (i + 1) * self.cell_size, size_of_board)

        for i in range(self.n - 1):
            self.canvas.create_line(0, (i + 1) * self.cell_size, size_of_board, (i + 1) * self.cell_size)

    def play_again(self):
        self.initialize_board()
        self.player_X_starts = not self.player_X_starts
        self.player_X_turns = self.player_X_starts
        self.board.reset()
        self.elapsed = 0
        if self.vs_ai and not self.player_X_turns:
            self.ai_move()

    def redraw(self):
        self.canvas.delete("all")
        self.initialize_board()
        for r, c in zip(*np.where(self.board.cells == -1)):
            self.draw_X((r, c))
        for r, c in zip(*np.where(self.board.cells == 1)):
            self.draw_O((r, c))

    def draw_O(self, logical_position):
        grid_position = self.convert_logical_to_grid_position(logical_position)
        self.canvas.create_oval(grid_position[0] - self.symbol_size, grid_position[1] - self.symbol_size,
                                grid_position[0] + self.symbol_size, grid_position[1] + self.symbol_size,
                                width=symbol_thickness, outline=symbol_O_color)

    def draw_X(self, logical_position):
        grid_position = self.convert_logical_to_grid_position(logical_position)
        self.canvas.create_line(grid_position[0] - self.symbol_size, grid_position[1] - self.symbol_size,
                                grid_position[0] + self.symbol_size, grid_position[1] + self.symbol_size,
                                width=symbol_thickness, fill=symbol_X_color)
        self.canvas.create_line(grid_position[0] - self.symbol_size, grid_position[1] + self.symbol_size,
                                grid_position[0] + self.symbol_size, grid_position[1] - self.symbol_size,
                                width=symbol_thickness, fill=symbol_X_color)

    def announce(self, text):
        os.system(f'say "{text}"')

    def display_gameover(self):
        if self.X_wins:
            self.X_score += 1
            text = f'Winner: {self.player_X_name} (X)'
            color = symbol_X_color
            storage.record_result(self.db, self.player_X_name, True)
            storage.record_result(self.db, self.player_O_name, False)
        elif self.O_wins:
            self.O_score += 1
            text = f'Winner: {self.player_O_name} (O)'
            color = symbol_O_color
            storage.record_result(self.db, self.player_O_name, True)
            storage.record_result(self.db, self.player_X_name, False)
        else:
            self.tie_score += 1
            text = 'Its a tie'
            color = 'gray'

        scores = {"X": self.X_score, "O": self.O_score, "tie": self.tie_score}
        storage.save_scores(scores)
        storage.upload_scores(scores, self.player_X_name)
        self.announce(text)

        self.canvas.delete("all")
        self.canvas.create_text(size_of_board / 2, size_of_board / 3, font="cmr 50 bold", fill=color, text=text)

        score_text = 'Scores \n'
        self.canvas.create_text(size_of_board / 2, 5 * size_of_board / 8, font="cmr 40 bold", fill=Green_color,
                                text=score_text)

        x_rate = storage.win_rate(self.db, self.player_X_name)
        o_rate = storage.win_rate(self.db, self.player_O_name)
        score_text = f'{self.player_X_name} (X) : {self.X_score} ({x_rate:.0%})\n'
        score_text += f'{self.player_O_name} (O): {self.O_score} ({o_rate:.0%})\n'
        score_text += 'Tie                    : ' + str(self.tie_score)
        self.canvas.create_text(size_of_board / 2, 3 * size_of_board / 4, font="cmr 30 bold", fill=Green_color,
                                text=score_text)
        self.reset_board = True

        score_text = 'Click to play again \n'
        self.canvas.create_text(size_of_board / 2, 15 * size_of_board / 16, font="cmr 20 bold", fill="gray",
                                text=score_text)

    def convert_logical_to_grid_position(self, logical_position):
        logical_position = np.array(logical_position, dtype=int)
        return self.cell_size * logical_position + self.cell_size / 2

    def convert_grid_to_logical_position(self, grid_position):
        grid_position = np.array(grid_position)
        return np.array(grid_position // self.cell_size, dtype=int)

    def is_gameover(self):
        winner = self.board.winner()
        self.X_wins = winner == -1
        self.O_wins = winner == 1
        self.tie = self.board.is_full()
        return self.X_wins or self.O_wins or self.tie

    def ai_move(self):
        row, col = self.ai.choose_move(self.board)
        self.board.place(row, col, 1)
        self.draw_O((row, col))
        self.player_X_turns = True
        if self.is_gameover():
            self.display_gameover()

    def undo(self, event=None):
        if self.reset_board:
            return
        self.board.undo()
        self.player_X_turns = not self.player_X_turns
        self.redraw()

    def save_session(self, event=None):
        state = {
            "cells": self.board.cells,
            "history": self.board.history,
            "player_X_turns": self.player_X_turns,
            "scores": (self.X_score, self.O_score, self.tie_score),
        }
        storage.save_session(f"sessions/{self.player_X_name}.session", state)

    def load_session(self, event=None):
        name = simpledialog.askstring("Load session", "Session name:")
        state = storage.load_session(f"sessions/{name}.session")
        self.board.cells = state["cells"]
        self.board.history = state["history"]
        self.player_X_turns = state["player_X_turns"]
        self.X_score, self.O_score, self.tie_score = state["scores"]
        self.redraw()

    def click(self, event):
        grid_position = [event.x, event.y]
        logical_position = self.convert_grid_to_logical_position(grid_position)
        row, col = logical_position[0], logical_position[1]

        if not self.reset_board:
            value = -1 if self.player_X_turns else 1
            if self.board.place(row, col, value):
                if self.player_X_turns:
                    self.draw_X(logical_position)
                else:
                    self.draw_O(logical_position)
                self.player_X_turns = not self.player_X_turns

            if self.is_gameover():
                self.display_gameover()
            elif self.vs_ai and not self.player_X_turns:
                self.ai_move()
        else:
            self.canvas.delete("all")
            self.play_again()
            self.reset_board = False


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    mode = sys.argv[2] if len(sys.argv) > 2 else "pvp"
    difficulty = sys.argv[3] if len(sys.argv) > 3 else "hard"
    game_instance = Tic_Tac_Toe(n=n, vs_ai=mode == "ai", difficulty=difficulty)
    game_instance.mainloop()
