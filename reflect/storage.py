from reflect.board import Board


def load_board(filename):
    with open(filename) as f:
        full_board = "".join([line for line in f.readlines()])
        return Board.create(full_board=full_board)


def save_board(board, filename, header=None):
    with open(filename, "w") as f:
        if header is not None:
            f.write(header)
        f.write(board.puzzle_solution())
        f.write("\n")
