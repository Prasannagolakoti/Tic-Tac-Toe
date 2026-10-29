"""Stateless Big Tic-Tac-Toe API, adapted from the uploaded Tkinter game."""
import math
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
EMPTY, HUMAN, AI = "", "X", "O"

class GameAI:
    def __init__(self, board, n, k):
        self.board, self.n, self.k = board[:], n, k
        self.lines = []
        for row in range(n):
            for col in range(n):
                for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
                    if 0 <= row + (k - 1) * dr < n and 0 <= col + (k - 1) * dc < n:
                        self.lines.append([(row + t * dr) * n + col + t * dc for t in range(k)])

    def winner(self):
        for line in self.lines:
            mark = self.board[line[0]]
            if mark and all(self.board[i] == mark for i in line):
                return mark, line
        return None, []

    def candidates(self):
        available = [i for i, v in enumerate(self.board) if v == EMPTY]
        if len(available) == self.n * self.n:
            return [(self.n // 2) * self.n + self.n // 2]
        moves = []
        for i in available:
            row, col = divmod(i, self.n)
            if any(self.board[r * self.n + c]
                   for r in range(max(0, row - 2), min(self.n, row + 3))
                   for c in range(max(0, col - 2), min(self.n, col + 3))):
                moves.append(i)
        return moves or available

    def evaluate(self):
        winner, _ = self.winner()
        if winner == AI:
            return 1_000_000
        if winner == HUMAN:
            return -1_000_000
        value = 0
        for line in self.lines:
            a = sum(self.board[i] == AI for i in line)
            h = sum(self.board[i] == HUMAN for i in line)
            if a and h:
                continue
            if a:
                value += 5 ** a
            elif h:
                value -= 5 ** h
        center = (self.n - 1) / 2
        for i, mark in enumerate(self.board):
            if mark:
                row, col = divmod(i, self.n)
                weight = self.n - abs(center - row) - abs(center - col)
                value += (1 if mark == AI else -1) * weight * 0.4
        return int(value)

    def search(self, turn, depth, max_depth, alpha, beta, stats):
        stats['nodes'] += 1
        winner, _ = self.winner()
        if winner or depth >= max_depth or EMPTY not in self.board:
            return self.evaluate()
        if turn == AI:
            best = -math.inf
            for move in self.candidates():
                self.board[move] = AI
                best = max(best, self.search(HUMAN, depth + 1, max_depth, alpha, beta, stats))
                self.board[move] = EMPTY
                alpha = max(alpha, best)
                if alpha >= beta:
                    stats['cuts'] += 1
                    break
            return int(best)
        best = math.inf
        for move in self.candidates():
            self.board[move] = HUMAN
            best = min(best, self.search(AI, depth + 1, max_depth, alpha, beta, stats))
            self.board[move] = EMPTY
            beta = min(beta, best)
            if alpha >= beta:
                stats['cuts'] += 1
                break
        return int(best)

    def choose_move(self, level):
        max_depth = {'Easy': 1, 'Medium': 2, 'Hard': 3}[level]
        if self.n >= 6:
            max_depth = min(max_depth, 2)
        stats = {'nodes': 0, 'cuts': 0}
        best_move, best_value = None, -math.inf
        for move in self.candidates():
            self.board[move] = AI
            value = self.search(HUMAN, 1, max_depth, -math.inf, math.inf, stats)
            self.board[move] = EMPTY
            if value > best_value:
                best_move, best_value = move, value
        return best_move, stats

@app.get('/api/health')
def health():
    return jsonify({'status': 'ok'})

@app.post('/api/move')
def move():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'error': 'Expected JSON object'}), 400
    board, n, k, level = (data.get(key) for key in ('board', 'n', 'k', 'level'))
    if (type(n) is not int or n not in (4, 5, 6, 7) or type(k) is not int
            or not 3 <= k <= n or level not in ('Easy', 'Medium', 'Hard')
            or not isinstance(board, list) or len(board) != n * n
            or any(v not in (EMPTY, HUMAN, AI) for v in board)):
        return jsonify({'error': 'Invalid game settings or board'}), 400
    xs, os = board.count(HUMAN), board.count(AI)
    if xs != os + 1:
        return jsonify({'error': 'Expected the human to play first and just complete a turn'}), 400
    game = GameAI(board, n, k)
    winner, line = game.winner()
    if winner or EMPTY not in board:
        return jsonify({'board': board, 'move': None, 'winner': winner, 'line': line, 'draw': not winner, 'nodes': 0, 'cuts': 0})
    ai_move, stats = game.choose_move(level)
    if ai_move is not None:
        game.board[ai_move] = AI
    winner, line = game.winner()
    return jsonify({'board': game.board, 'move': ai_move, 'winner': winner,
                    'line': line, 'draw': not winner and EMPTY not in game.board,
                    'nodes': stats['nodes'], 'cuts': stats['cuts']})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
