from reflect.board import Board


def load_board(filename):
    with open(filename) as f:
        full_board = "".join([line for line in f.readlines()])
        return Board.create(full_board=full_board)
