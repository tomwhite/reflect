from blessed import Terminal

from reflect import Board


class Game:
    """Play an interactive game of reflect"""

    def __init__(self, term, board):
        self.term = term
        self.board = board
        self.n = board.n
        self.size = board.n + 2
        self.x = 0
        self.y = 0

    def print_board(self):
        print(self.term.move_xy(0, 0) + str(self.board))

    def print_message(self, message):
        print(self.term.move_xy(0, self.n * 2 - 1) + f"{message:<{80}}")

    def clear_message(self):
        print(self.term.move_xy(0, self.n * 2 - 1) + (" " * 80))

    def move_cursor(self, dx, dy):
        self.clear_char()
        self.x += dx
        self.y += dy
        self.reverse_char()

    def get_char_at(self):
        length = self.size + 1
        return str(self.board)[self.y * length + self.x]

    def clear_char(self):
        print(self.term.move_xy(self.x, self.y) + self.get_char_at())

    def reverse_char(self):
        print(self.term.move_xy(self.x, self.y) + self.term.reverse(self.get_char_at()))

    def set_value(self, value):
        if board.on_inner_board(self.x, self.y):
            self.board.set_value(self.x, self.y, value)
            self.print_board()
            self.reverse_char()

    def beam(self):
        if board.on_edge(self.x, self.y):
            self.board.beam(self.x, self.y)
            self.print_board()
            self.reverse_char()

    def play(self):
        with self.term.fullscreen(), self.term.hidden_cursor():
            self.print_board()
            self.reverse_char()
            with self.term.cbreak():
                val = ""
                while val.lower() != "q":
                    val = self.term.inkey()
                    if val.code == self.term.KEY_LEFT and self.x > 0:
                        self.move_cursor(-1, 0)
                    elif val.code == self.term.KEY_RIGHT and self.x < self.size - 1:
                        self.move_cursor(1, 0)
                    elif val.code == self.term.KEY_UP and self.y > 0:
                        self.move_cursor(0, -1)
                    elif val.code == self.term.KEY_DOWN and self.y < self.size - 1:
                        self.move_cursor(0, 1)
                    elif val == " ":
                        self.beam()
                    elif val in (".", "/", "\\"):
                        self.set_value(val)
                    elif val == "s":
                        s = self.board.score()
                        self.print_message(f"Score: {s}")


if __name__ == "__main__":
    blocks = """
....
../\\
.../
....
"""
    board = Board.create(hidden_blocks=blocks)
    term = Terminal()
    game = Game(term, board)
    game.play()
