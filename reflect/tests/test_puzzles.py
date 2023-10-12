import datetime
from pathlib import Path

import pytest

from reflect import Board, boards_are_unique, has_unique_solution, solve
from reflect.storage import first_missing_puzzle_path, load_board


def test_puzzles_have_unique_solution(request):
    today = datetime.datetime.today()
    start_date = (today - datetime.timedelta(days=2)).strftime("%Y-%m-%d")
    end_date = (today + datetime.timedelta(days=5)).strftime("%Y-%m-%d")
    start_puzzle = f"puzzle-{start_date}.txt"
    end_puzzle = f"puzzle-{end_date}.txt"
    for full_board_file in sorted((request.config.rootdir / "puzzles").listdir()):
        if full_board_file.isfile():
            filename = Path(full_board_file).name
            if filename < start_puzzle or filename > end_puzzle:
                continue  # only test a week's worth of puzzles
            board = load_board(full_board_file)
            assert has_unique_solution(board)

            # extra stringent checks for later puzzles
            if filename > "puzzle-2023-04-17.txt" and filename != "puzzle-help.txt":
                assert has_unique_solution(
                    board,
                    fewer_pieces_allowed=True,
                    ball_on_two_ended_beam_allowed=True,
                )


@pytest.mark.parametrize(
    "full_board",
    [
        """
..B...
......
Do\\..B
C./...
......
.A....
""",
        """
.AAC..
B.\\.\\.
B./..D
.\\../F
E....E
..DCF.
""",
        """
.DEIL.
H..\\oJ
D//..G
C..o.K
A.../B
.EGFB.
""",
    ],
)
def test_not_unique_solution(full_board):
    board = Board.create(full_board=full_board)
    solutions = solve(board)
    assert len(solutions) > 1


def test_puzzle_boards_are_unique(request):
    boards = []
    for full_board_file in (request.config.rootdir / "puzzles").listdir():
        if full_board_file.isfile():
            board = load_board(full_board_file)
            boards.append(board)
    assert boards_are_unique(boards)


def test_boards_are_unique():
    full_board = """
..B...
./....
D....B
C.....
...o..
.A....
"""
    board = Board.create(full_board=full_board)
    boardRot90 = board.rot90()

    assert boards_are_unique([board, boardRot90], include_transforms=False)
    assert not boards_are_unique([board, boardRot90], include_transforms=True)


def test_boards_are_unique_symmetric():
    full_board1 = """
..B...
./....
D....B
C.....
...o..
.A....
"""

    # this board is symmetric (but different to board 1)
    full_board2 = """
..B...
./....
D.....B
C.....
..../.
.A....
"""
    board1 = Board.create(full_board=full_board1)
    board2 = Board.create(full_board=full_board2)

    assert boards_are_unique([board1, board2], include_transforms=False)
    assert boards_are_unique([board1, board2], include_transforms=True)


def test_puzzles_in_future(request):
    day = datetime.datetime.today()
    num_days = 0
    while True:
        date = day.strftime("%Y-%m-%d")
        full_board_file = request.config.rootdir / "puzzles" / f"puzzle-{date}.txt"
        if not full_board_file.exists():
            break
        load_board(full_board_file)
        num_days += 1
        day = day + datetime.timedelta(days=1)
    assert num_days >= 3, f"Missing {full_board_file}"
    assert first_missing_puzzle_path().name == Path(full_board_file).name
