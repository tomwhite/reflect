import pytest

from reflect import Board, boards_are_unique, solve


def test_puzzles_have_unique_solution(request):
    for full_board_file in (request.config.rootdir / "puzzles").listdir():
        with open(full_board_file) as f:
            full_board = "".join(
                [line for line in f.readlines() if not line.startswith("#")]
            )
            full_board = full_board.strip()

            board = Board.create(full_board=full_board)
            beams = board.beams
            pieces = board.pieces_ints

            solutions = solve(beams, pieces)
            assert len(solutions) == 1


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
    beams = board.beams
    pieces = board.pieces_ints

    solutions = solve(beams, pieces)
    assert len(solutions) > 1


def test_puzzle_boards_are_unique(request):
    boards = []
    for full_board_file in (request.config.rootdir / "puzzles").listdir():
        if str(full_board_file).endswith("puzzle-003.txt"):
            # ignore this puzzle as it shows an example with the same hidden blocks as puzzle-002, but different clues
            continue
        with open(full_board_file) as f:
            full_board = "".join(
                [line for line in f.readlines() if not line.startswith("#")]
            )
            full_board = full_board.strip()

            board = Board.create(full_board=full_board)
            boards.append(board)
    assert boards_are_unique(boards)


def test_boards_are_unique():
    full_board = """
..B...
./....
D.....B
C.....
...o..
.A....
"""
    board = Board.create(full_board=full_board)
    boardRot90 = board.rot90()

    assert boards_are_unique([board, boardRot90], include_transforms=False)
    assert not boards_are_unique([board, boardRot90], include_transforms=True)
