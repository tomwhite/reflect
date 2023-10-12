import datetime
from pathlib import Path

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


def first_missing_puzzle_path(puzzles_dir="puzzles"):
    """Return the path for the next puzzle to be set."""
    day = datetime.datetime.today()
    num_days = 0
    while True:
        date = day.strftime("%Y-%m-%d")
        full_board_file = Path("puzzles") / f"puzzle-{date}.txt"
        if not full_board_file.exists():
            return full_board_file
        num_days += 1
        day = day + datetime.timedelta(days=1)


def board_generator_from_files(dir="puzzles/generated"):
    dir_path = Path(dir)
    for f in sorted(dir_path.iterdir()):
        yield load_board(f)
