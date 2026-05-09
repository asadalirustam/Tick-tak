import os
import sys
import random
import json

# Fix Windows terminal Unicode encoding
sys.stdout.reconfigure(encoding="utf-8")


# ─── Board Class ─────────────────────────────────────────────────────────────
class Board:
    def __init__(self):
        self.grid = [[" " for _ in range(3)] for _ in range(3)]

    def display(self):
        os.system("cls" if os.name == "nt" else "clear")
        print("\n  ╔═══════════════╗")
        print("  ║  TIC-TAC-TOE  ║")
        print("  ╚═══════════════╝\n")

        print("  (Positions: 1-9)\n")
        print(f"    1 │ 2 │ 3       ┌───┬───┬───┐")
        print(f"   ───┼───┼───      │", end="")

        for col in range(3):
            cell = self.grid[0][col]
            print(f" {cell} │", end="")

        print(f"\n    4 │ 5 │ 6       ├───┼───┼───┤")
        print(f"   ───┼───┼───      │", end="")

        for col in range(3):
            cell = self.grid[1][col]
            print(f" {cell} │", end="")

        print(f"\n    7 │ 8 │ 9       ├───┼───┼───┤")
        print(f"                    │", end="")

        for col in range(3):
            cell = self.grid[2][col]
            print(f" {cell} │", end="")

        print(f"\n                    └───┴───┴───┘\n")

    def make_move(self, position, symbol):
        """Position: 1-9"""
        row = (position - 1) // 3
        col = (position - 1) % 3
        if self.grid[row][col] == " ":
            self.grid[row][col] = symbol
            return True
        return False

    def check_winner(self, symbol):
        g = self.grid
        # Rows
        for row in g:
            if all(cell == symbol for cell in row):
                return True
        # Columns
        for col in range(3):
            if all(g[row][col] == symbol for row in range(3)):
                return True
        # Diagonals
        if all(g[i][i] == symbol for i in range(3)):
            return True
        if all(g[i][2 - i] == symbol for i in range(3)):
            return True
        return False

    def is_full(self):
        return all(self.grid[r][c] != " " for r in range(3) for c in range(3))

    def available_moves(self):
        return [
            r * 3 + c + 1
            for r in range(3)
            for c in range(3)
            if self.grid[r][c] == " "
        ]

    def reset(self):
        self.grid = [[" " for _ in range(3)] for _ in range(3)]


# ─── Player Classes ──────────────────────────────────────────────────────────
class Player:
    def __init__(self, name, symbol):
        self.name = name
        self.symbol = symbol
        self.score = 0

    def get_move(self, board):
        raise NotImplementedError


class HumanPlayer(Player):
    def get_move(self, board):
        while True:
            try:
                move = int(input(f"  {self.name} ({self.symbol}), enter position (1-9): "))
                if move in board.available_moves():
                    return move
                else:
                    print("  Invalid or already taken! Try again.")
            except ValueError:
                print("  Please enter a number 1-9.")


class AIPlayer(Player):
    """AI using Minimax algorithm — unbeatable!"""

    def get_move(self, board):
        print("  AI is thinking...")
        best_score = -float("inf")
        best_move = None
        for move in board.available_moves():
            board.make_move(move, self.symbol)
            score = self._minimax(board, False)
            board.grid[(move - 1) // 3][(move - 1) % 3] = " "
            if score > best_score:
                best_score = score
                best_move = move
        return best_move

    def _minimax(self, board, is_maximizing):
        opp_symbol = "O" if self.symbol == "X" else "X"

        if board.check_winner(self.symbol):
            return 1
        if board.check_winner(opp_symbol):
            return -1
        if board.is_full():
            return 0

        if is_maximizing:
            best = -float("inf")
            for move in board.available_moves():
                board.make_move(move, self.symbol)
                best = max(best, self._minimax(board, False))
                board.grid[(move - 1) // 3][(move - 1) % 3] = " "
            return best
        else:
            best = float("inf")
            for move in board.available_moves():
                board.make_move(move, opp_symbol)
                best = min(best, self._minimax(board, True))
                board.grid[(move - 1) // 3][(move - 1) % 3] = " "
            return best


# ─── Game Class ──────────────────────────────────────────────────────────────
class Game:
    def __init__(self):
        self.board = Board()
        self.player1 = None
        self.player2 = None
        self.current_player = None
        self.score_file = "scores.json"
        self.all_scores = self.load_scores()

    def load_scores(self):
        if os.path.exists(self.score_file):
            try:
                with open(self.score_file, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

    def save_scores(self):
        if self.player1:
            self.all_scores[self.player1.name] = self.player1.score
        if self.player2:
            self.all_scores[self.player2.name] = self.player2.score
        with open(self.score_file, "w") as f:
            json.dump(self.all_scores, f, indent=4)

    def setup(self):
        os.system("cls" if os.name == "nt" else "clear")
        print("\n  ╔══════════════════════════╗")
        print("  ║   🎮  TIC-TAC-TOE  🎮    ║")
        print("  ╚══════════════════════════╝\n")

        # Game mode
        print("  Select Game Mode:")
        print("  1. Player vs Player")
        print("  2. Player vs AI (Unbeatable)")

        while True:
            mode = input("\n  Enter choice (1 or 2): ").strip()
            if mode in ("1", "2"):
                break
            print("  Invalid choice!")

        # Player 1
        p1_name = input("\n  Player 1 name (X): ").strip() or "Player 1"
        self.player1 = HumanPlayer(p1_name, "X")

        if mode == "1":
            p2_name = input("  Player 2 name (O): ").strip() or "Player 2"
            self.player2 = HumanPlayer(p2_name, "O")
        else:
            self.player2 = AIPlayer("AI Bot", "O")

        # Load existing scores for the current players
        self.player1.score = self.all_scores.get(self.player1.name, 0)
        self.player2.score = self.all_scores.get(self.player2.name, 0)

        self.current_player = self.player1

    def switch_player(self):
        self.current_player = (
            self.player2 if self.current_player == self.player1 else self.player1
        )

    def display_scores(self):
        print("  Scores:")
        print(f"  {self.player1.name}: {self.player1.score}  |  {self.player2.name}: {self.player2.score}\n")

    def play_round(self):
        self.board.reset()
        self.current_player = self.player1

        while True:
            self.board.display()
            self.display_scores()

            move = self.current_player.get_move(self.board)
            self.board.make_move(move, self.current_player.symbol)

            if self.board.check_winner(self.current_player.symbol):
                self.current_player.score += 1
                self.save_scores()
                self.board.display()
                self.display_scores()
                print(f"  {self.current_player.name} Wins!\n")
                return

            if self.board.is_full():
                self.board.display()
                self.display_scores()
                print("  It's a Draw!\n")
                return

            self.switch_player()

    def play(self):
        self.setup()

        while True:
            self.play_round()

            again = input("  Play again? (y/n): ").strip().lower()
            if again != "y":
                print("\n  Thanks for playing!\n")
                break


# ─── Entry Point ─────────────────────────────────────────────────────────────
def main():
    game = Game()
    game.play()


if __name__ == "__main__":
    main()
