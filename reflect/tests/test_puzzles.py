import pytest

from reflect import Board, boards_are_unique, has_unique_solution, solve


def test_puzzles_have_unique_solution(request):
    for full_board_file in (request.config.rootdir / "puzzles").listdir():
        if full_board_file.isfile():
            with open(full_board_file) as f:
                full_board = "".join([line for line in f.readlines()])
                board = Board.create(full_board=full_board)
                assert has_unique_solution(board)


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
            with open(full_board_file) as f:
                full_board = "".join([line for line in f.readlines()])
                board = Board.create(full_board=full_board)
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
