import pytest

from reflect import *

def test_unique(request):
    for full_board_file in (request.config.rootdir / "puzzles").listdir():
        with open(full_board_file) as f:
            full_board = "".join([line for line in f.readlines() if not line.startswith("#")])
            full_board = full_board.strip()

            board = Board.create(full_board=full_board)
            beams = board.beams
            pieces = board.pieces_ints

            solutions = solve(beams, pieces)
            assert len(solutions) == 1


@pytest.mark.parametrize("full_board", [
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
])
def test_not_unique(full_board):
    board = Board.create(full_board=full_board)
    beams = board.beams
    pieces = board.pieces_ints

    solutions = solve(beams, pieces)
    assert len(solutions) > 1
