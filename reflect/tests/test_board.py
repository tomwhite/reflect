import numpy as np
from numpy.testing import assert_array_equal

from reflect import Board


def test_board():
    # note we have to escape a backslash
    blocks = """
....
../\\
.../
....
"""
    board = Board.create(hidden_blocks=blocks)
    assert_array_equal(
        board.values,
        np.array(
            [
                [".", ".", ".", ".", ".", "."],
                [".", ".", ".", ".", ".", "."],
                [".", ".", ".", ".", ".", "."],
                [".", ".", ".", ".", ".", "."],
                [".", ".", ".", ".", ".", "."],
                [".", ".", ".", ".", ".", "."],
            ]
        ),
    )

    # assert str(board).strip() == blocks.strip()

    # corners
    assert board.on_edge(0, 0) is False
    assert board.on_edge(0, 5) is False
    assert board.on_edge(5, 0) is False
    assert board.on_edge(5, 5) is False

    assert board.on_inner_board(0, 0) is False
    assert board.on_inner_board(0, 5) is False
    assert board.on_inner_board(5, 0) is False
    assert board.on_inner_board(5, 5) is False

    # inner board
    assert board.on_edge(1, 1) is False
    assert board.on_edge(2, 1) is False

    assert board.on_inner_board(1, 1) is True
    assert board.on_inner_board(2, 1) is True

    # edges
    assert board.on_edge(1, 0) is True
    assert board.on_edge(0, 1) is True
    assert board.on_edge(4, 0) is True
    assert board.on_edge(0, 4) is True
    assert board.on_edge(1, 5) is True
    assert board.on_edge(5, 1) is True
    assert board.on_edge(4, 5) is True
    assert board.on_edge(5, 4) is True

    assert board.on_inner_board(1, 0) is False
    assert board.on_inner_board(0, 1) is False

    # hidden_board_ints
    assert_array_equal(
        board.hidden_blocks_ints,
        np.array(
            [
                [0, 0, 0, 0],
                [0, 0, 1, 2],
                [0, 0, 0, 1],
                [0, 0, 0, 0],
            ]
        ),
    )


def test_full_board():
    full_board = """
....A.
......
......
.../\\A
B....B
...CC.
"""
    board = Board.create(full_board=full_board)
    # check that inner board does not show hidden blocks
    assert_array_equal(
        board.values,
        np.array(
            [
                [".", ".", ".", ".", "A", "."],
                [".", ".", ".", ".", ".", "."],
                [".", ".", ".", ".", ".", "."],
                [".", ".", ".", ".", ".", "A"],
                ["B", ".", ".", ".", ".", "B"],
                [".", ".", ".", "C", "C", "."],
            ]
        ),
    )

    # note that the puzzle string doesn't show hidden blocks
    assert (
        board.puzzle_string()
        == """....A.
......
......
.....A
B....B
...CC.

Blocks: /\\"""
    )

    assert board.puzzle_solution().strip() == full_board.strip()

    boardRot90 = board.rot90()

    # fmt: off
    assert_array_equal(
        boardRot90.values,
        np.array(
            [
                [".", ".", ".", "A", "B", "."],
                ["A", ".", ".", ".", ".", "C"],
                [".", ".", ".", ".", ".", "C"],
                [".", ".", ".", ".", ".", "."],
                [".", ".", ".", ".", ".", "."],
                [".", ".", ".", ".", "B", "."],
            ]
        ),
    )

    # note that mirrors are rotated too
    assert_array_equal(
        boardRot90.hidden_blocks,
        np.array(
            [
                [".", ".", "/", "."],
                [".", ".", "\\", "."],
                [".", ".", ".", "."],
                [".", ".", ".", "."],
            ]
        ),
    )

    assert_array_equal(
        board.beams,
        np.array([
            [3, -1, 4, 2],
            [-1, 3, 4, 3],
            [2, 4, 3, 4],
        ], dtype=np.int8),
    )
    # fmt: on


def test_add_beam():
    blocks = """
....
../\\
.../
....
"""
    board = Board.create(hidden_blocks=blocks)
    assert_array_equal(board.pieces, ["/", "/", "\\"])
    path = board.add_beam(0, 1)
    assert_array_equal(path[-1], [5, 1])
    path = board.add_beam(0, 2)
    assert_array_equal(path[-1], [3, 0])
    path = board.add_beam(0, 3)
    assert_array_equal(path[-1], [3, 5])
    path = board.add_beam(1, 0)
    assert_array_equal(path[-1], [1, 5])
    path = board.add_beam(4, 0)
    assert_array_equal(path[-1], [5, 2])

    assert board.num_beams == 5
    assert len(board.beam_paths) == 5

    board.remove_beam(0, 1)

    assert board.num_beams == 4
    assert len(board.beam_paths) == 4


def test_edge_locations():
    blocks = """
....
../\\
.../
....
"""
    board = Board.create(hidden_blocks=blocks)
    for x, y in board.edge_locations():
        assert board.on_edge(x, y)
        assert not board.on_inner_board(x, y)
