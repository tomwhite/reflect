from reflect.board import Board
from reflect.difficulty import board_features


def test_board_features():
    full_board = """
......
Do...J
E..\\/H
..\\...
G/../.
.H.E..
"""
    board = Board.create(full_board=full_board)

    features = board_features(board)

    assert features["num_blocks"] == 6
    assert features["num_mirror_balls"] == 1
    assert features["max_blocks_per_beam"] == 3
    assert features["max_beams_per_block"] == 3
    assert features["num_zero_reflection_blocks"] == 1
