"""Big Tic-Tac-Toe graphical game with animated marks and Minimax AI."""

from __future__ import annotations

import math
import random
import tkinter as tk
from tkinter import ttk

EMPTY, HUMAN, AI = "", "X", "O"
BG = "#101827"
PANEL = "#172338"
CELL = "#1d2b41"
GRID = "#415875"
CYAN = "#67e8f9"
PURPLE = "#c4b5fd"
GOLD = "#fbbf24"


class BigTicTacToe:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Big Tic-Tac-Toe · Minimax AI")
        self.root.configure(bg=BG)
        self.root.minsize(620, 690)
        self.n = 5
        self.k = 4
        self.board = [EMPTY] * (self.n * self.n)
        self.finished = False
        self.busy = False
        self.lines: list[list[int]] = []
        self.cell = 80
        self.pad = 12
        self.canvas_size = 5 * self.cell + 2 * self.pad
        self._style()
        self._build_ui()
        self.new_game()

    def _style(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TCombobox", fieldbackground="#24344e", background="#24344e",
                        foreground="#f0f6ff", arrowcolor="#f0f6ff")

    def _build_ui(self) -> None:
        outer = tk.Frame(self.root, bg=PANEL, padx=22, pady=18)
        outer.pack(fill="both", expand=True, padx=18, pady=18)
        tk.Label(outer, text="AI MINI-CAPSTONE · ADVERSARIAL SEARCH", bg=PANEL,
                 fg=CYAN, font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(outer, text="Big Tic-Tac-Toe", bg=PANEL, fg="#f4f7fb",
                 font=("Segoe UI", 24, "bold")).pack(anchor="w", pady=(3, 0))
        tk.Label(outer, text="Play on a larger board against a Minimax opponent.", bg=PANEL,
                 fg="#aebed3", font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 14))

        controls = tk.Frame(outer, bg=PANEL)
        controls.pack(fill="x", pady=(0, 12))
        self.size_var = tk.StringVar(value="5")
        self.target_var = tk.StringVar(value="4")
        self.level_var = tk.StringVar(value="Medium")
        self._selector(controls, "BOARD", self.size_var, ["4", "5", "6", "7"])
        self._selector(controls, "WIN LENGTH", self.target_var, ["3", "4", "5", "6", "7"])
        self._selector(controls, "AI DEPTH", self.level_var, ["Easy", "Medium", "Hard"])
        tk.Button(controls, text="New Game", command=self.new_game, bg="#0e7490", fg="white",
                  activebackground="#0891b2", activeforeground="white", relief="flat",
                  font=("Segoe UI", 10, "bold"), padx=14, pady=7, cursor="hand2").pack(side="right", padx=(6, 0), pady=(14, 0))

        self.status = tk.Label(outer, text="", bg=PANEL, fg="#f0f6ff",
                               font=("Segoe UI", 11, "bold"), anchor="w")
        self.status.pack(fill="x", pady=(0, 8))
        self.canvas = tk.Canvas(outer, width=self.canvas_size, height=self.canvas_size,
                                bg="#111c2d", highlightthickness=1, highlightbackground="#334963")
        self.canvas.pack(pady=(0, 12))
        self.canvas.bind("<Button-1>", self.on_click)
        bottom = tk.Frame(outer, bg=PANEL)
        bottom.pack(fill="x")
        self.nodes_label = tk.Label(bottom, text="Positions searched: 0", bg=PANEL,
                                    fg="#c3d1e3", font=("Segoe UI", 9))
        self.nodes_label.pack(side="left")
        self.cutoff_label = tk.Label(bottom, text="Pruned branches: 0", bg=PANEL,
                                     fg="#c3d1e3", font=("Segoe UI", 9))
        self.cutoff_label.pack(side="right")
        tk.Label(outer, text="You: X   ·   AI: O   ·   Larger boards use heuristic, depth-limited search.",
                 bg=PANEL, fg="#8093ad", font=("Segoe UI", 8)).pack(anchor="w", pady=(10, 0))

    @staticmethod
    def _selector(parent: tk.Frame, label: str, variable: tk.StringVar, values: list[str]) -> None:
        group = tk.Frame(parent, bg=PANEL)
        group.pack(side="left", padx=(0, 12), pady=(0, 0))
        tk.Label(group, text=label, bg=PANEL, fg="#8295ad", font=("Segoe UI", 7, "bold")).pack(anchor="w")
        combo = ttk.Combobox(group, textvariable=variable, values=values, state="readonly", width=10)
        combo.pack()
        combo.bind("<<ComboboxSelected>>", lambda _event: None)

    def _make_lines(self) -> list[list[int]]:
        result: list[list[int]] = []
        for row in range(self.n):
            for col in range(self.n):
                for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
                    end_r, end_c = row + (self.k - 1) * dr, col + (self.k - 1) * dc
                    if not (0 <= end_r < self.n and 0 <= end_c < self.n):
                        continue
                    result.append([(row + t * dr) * self.n + col + t * dc for t in range(self.k)])
        return result

    def new_game(self) -> None:
        self.n = int(self.size_var.get())
        self.k = min(int(self.target_var.get()), self.n)
        self.target_var.set(str(self.k))
        self.lines = self._make_lines()
        self.board = [EMPTY] * (self.n * self.n)
        self.finished = self.busy = False
        self.cell = min(88, max(48, 480 // self.n))
        self.pad = 12
        self.canvas_size = self.n * self.cell + 2 * self.pad
        self.canvas.config(width=self.canvas_size, height=self.canvas_size)
        self.nodes_label.config(text="Positions searched: 0")
        self.cutoff_label.config(text="Pruned branches: 0")
        self.status.config(text=f"Get {self.k} in a row to win. Your turn.")
        self.draw_board()

    def draw_board(self) -> None:
        self.canvas.delete("all")
        for row in range(self.n):
            for col in range(self.n):
                x1 = self.pad + col * self.cell + 3
                y1 = self.pad + row * self.cell + 3
                x2, y2 = x1 + self.cell - 6, y1 + self.cell - 6
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=CELL, outline=GRID, width=1,
                                             tags=f"cell-{row * self.n + col}")
                mark = self.board[row * self.n + col]
                if mark:
                    color = CYAN if mark == HUMAN else PURPLE
                    self._draw_mark(row, col, mark, color)

    def _draw_mark(self, row: int, col: int, mark: str, color: str, scale: float = 1.0) -> None:
        cx = self.pad + col * self.cell + self.cell / 2
        cy = self.pad + row * self.cell + self.cell / 2
        radius = self.cell * 0.28 * scale
        if mark == HUMAN:
            self.canvas.create_line(cx - radius, cy - radius, cx + radius, cy + radius,
                                    fill=color, width=max(3, self.cell * 0.075), capstyle="round")
            self.canvas.create_line(cx + radius, cy - radius, cx - radius, cy + radius,
                                    fill=color, width=max(3, self.cell * 0.075), capstyle="round")
        else:
            self.canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius,
                                    outline=color, width=max(3, self.cell * 0.075))

    def on_click(self, event: tk.Event) -> None:
        if self.finished or self.busy:
            return
        col = int((event.x - self.pad) // self.cell)
        row = int((event.y - self.pad) // self.cell)
        if not (0 <= row < self.n and 0 <= col < self.n):
            return
        index = row * self.n + col
        if self.board[index]:
            return
        self.board[index] = HUMAN
        self.animate_mark(row, col, HUMAN, CYAN)
        if self._complete_check():
            return
        self.busy = True
        self.status.config(text="AI is thinking…")
        self.root.after(120, self.ai_turn)

    def animate_mark(self, row: int, col: int, mark: str, color: str) -> None:
        steps = 5
        def frame(step: int) -> None:
            self.draw_board()
            self.canvas.delete("mark-temp")
            cx = self.pad + col * self.cell + self.cell / 2
            cy = self.pad + row * self.cell + self.cell / 2
            radius = self.cell * 0.28 * (step / steps)
            if mark == HUMAN:
                self.canvas.create_line(cx - radius, cy - radius, cx + radius, cy + radius,
                                        fill=color, width=max(3, self.cell * 0.075), capstyle="round", tags="mark-temp")
                self.canvas.create_line(cx + radius, cy - radius, cx - radius, cy + radius,
                                        fill=color, width=max(3, self.cell * 0.075), capstyle="round", tags="mark-temp")
            else:
                self.canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius,
                                        outline=color, width=max(3, self.cell * 0.075), tags="mark-temp")
            if step < steps:
                self.root.after(24, lambda: frame(step + 1))
        frame(1)

    def _winner(self, board: list[str] | None = None) -> tuple[str | None, list[int] | None]:
        state = board if board is not None else self.board
        for line in self.lines:
            mark = state[line[0]]
            if mark and all(state[i] == mark for i in line):
                return mark, line
        return None, None

    def _complete_check(self) -> bool:
        mark, line = self._winner()
        if mark:
            self.finished = True
            self.status.config(text="You win! 🎉" if mark == HUMAN else "AI wins this round.")
            self.draw_board()
            self._highlight(line or [])
            return True
        if EMPTY not in self.board:
            self.finished = True
            self.status.config(text="It's a draw!")
            return True
        return False

    def _highlight(self, line: list[int]) -> None:
        for index in line:
            row, col = divmod(index, self.n)
            x1 = self.pad + col * self.cell + 3
            y1 = self.pad + row * self.cell + 3
            self.canvas.create_rectangle(x1, y1, x1 + self.cell - 6, y1 + self.cell - 6,
                                         outline=GOLD, width=4)

    def ai_turn(self) -> None:
        if self.finished:
            self.busy = False
            return
        move, nodes, cuts = self.choose_move()
        if move is None:
            self.busy = False
            return
        self.board[move] = AI
        row, col = divmod(move, self.n)
        self.nodes_label.config(text=f"Positions searched: {nodes:,}")
        self.cutoff_label.config(text=f"Pruned branches: {cuts:,}")
        self.busy = False
        self.animate_mark(row, col, AI, PURPLE)
        self.root.after(150, self._complete_check)
        if not self.finished:
            self.status.config(text="Your turn.")

    def choose_move(self) -> tuple[int | None, int, int]:
        level = self.level_var.get()
        max_depth = {"Easy": 1, "Medium": 2, "Hard": 3}[level]
        # The 7x7 board can have a large branching factor; cap its search depth.
        if self.n >= 6:
            max_depth = min(max_depth, 2)
        moves = self._candidate_moves()
        if not moves:
            return None, 0, 0
        stats = {"nodes": 0, "cuts": 0}
        best_move, best_value = moves[0], -math.inf
        for move in moves:
            self.board[move] = AI
            value = self._search(HUMAN, 1, max_depth, -math.inf, math.inf, stats)
            self.board[move] = EMPTY
            if value > best_value:
                best_value, best_move = value, move
        return best_move, stats["nodes"], stats["cuts"]

    def _candidate_moves(self) -> list[int]:
        available = [i for i, value in enumerate(self.board) if value == EMPTY]
        if all(value == EMPTY for value in self.board):
            return [(self.n // 2) * self.n + self.n // 2]
        candidates = []
        for i in available:
            row, col = divmod(i, self.n)
            if any(self.board[r * self.n + c]
                   for r in range(max(0, row - 2), min(self.n, row + 3))
                   for c in range(max(0, col - 2), min(self.n, col + 3))):
                candidates.append(i)
        return candidates or available

    def _evaluate(self) -> int:
        win, _ = self._winner()
        if win == AI:
            return 1_000_000
        if win == HUMAN:
            return -1_000_000
        value = 0
        for line in self.lines:
            ai_count = sum(self.board[i] == AI for i in line)
            human_count = sum(self.board[i] == HUMAN for i in line)
            if ai_count and human_count:
                continue
            if ai_count:
                value += 5 ** ai_count
            elif human_count:
                value -= 5 ** human_count
        center = (self.n - 1) / 2
        for i, mark in enumerate(self.board):
            if mark:
                row, col = divmod(i, self.n)
                weight = self.n - abs(center - row) - abs(center - col)
                value += (1 if mark == AI else -1) * weight * 0.4
        return int(value)

    def _search(self, turn: str, depth: int, max_depth: int, alpha: float,
                beta: float, stats: dict[str, int]) -> int:
        stats["nodes"] += 1
        win, _ = self._winner()
        if win or depth >= max_depth or EMPTY not in self.board:
            return self._evaluate()
        moves = self._candidate_moves()
        if turn == AI:
            best = -math.inf
            for move in moves:
                self.board[move] = AI
                best = max(best, self._search(HUMAN, depth + 1, max_depth, alpha, beta, stats))
                self.board[move] = EMPTY
                alpha = max(alpha, best)
                if alpha >= beta:
                    stats["cuts"] += 1
                    break
            return int(best)
        best = math.inf
        for move in moves:
            self.board[move] = HUMAN
            best = min(best, self._search(AI, depth + 1, max_depth, alpha, beta, stats))
            self.board[move] = EMPTY
            beta = min(beta, best)
            if alpha >= beta:
                stats["cuts"] += 1
                break
        return int(best)


def main() -> None:
    root = tk.Tk()
    BigTicTacToe(root)
    root.mainloop()


if __name__ == "__main__":
    main()
