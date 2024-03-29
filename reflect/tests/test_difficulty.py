from reflect.board import Board
from reflect.difficulty import board_features, minimum_blocks_on_path


def test_board_features():
    # set on 5 May 2023
    full_board = """
.ABCD.
E\\\\..B
C../..
E/\\.\\D
F...oJ
....I.
"""
    board = Board.create(full_board=full_board)

    features = board_features(board)

    assert features["num_blocks"] == 7
    assert features["num_mirror_balls"] == 1
    assert features["num_beams"] == 8
    assert features["num_reflections"] == 9
    assert features["mean_blocks_per_beam"] == 13 / 8
    assert features["max_blocks_per_beam"] == 5  # red
    assert features["num_multi_block_beams"] == 2
    assert features["mean_beams_per_block"] == 13 / 7
    assert features["max_beams_per_block"] == 4
    assert features["num_double_reflect_blocks"] == 3
    assert features["mean_beam_distance"] == 30 / 8
    assert features["max_beam_distance"] == 7  # red
    assert features["total_beam_distance"] == 30
    assert features["excess_beam_distance"] == 0
    assert features["num_zero_reflection_blocks"] == 0
    assert features["excess_reflections"] == 3
    assert features["num_excess_reflection_beams"] == 1
    assert features["num_beam_edges"] == 12

    # set on 6 May 2023
    full_board = """
.AB.D.
B./..A
......
F\\/..H
.\\.o.J
..HID.
"""
    board = Board.create(full_board=full_board)

    features = board_features(board)

    assert features["num_blocks"] == 5
    assert features["num_mirror_balls"] == 1
    assert features["num_beams"] == 7
    assert features["num_reflections"] == 7
    assert features["mean_blocks_per_beam"] == 10 / 7
    assert features["max_blocks_per_beam"] == 3  # red, blue
    assert features["num_multi_block_beams"] == 2
    assert features["mean_beams_per_block"] == 10 / 5
    assert features["max_beams_per_block"] == 3
    assert features["num_double_reflect_blocks"] == 3
    assert features["mean_beam_distance"] == 29 / 7
    assert features["max_beam_distance"] == 9  # red
    assert features["total_beam_distance"] == 29
    assert features["excess_beam_distance"] == 4
    assert features["num_zero_reflection_blocks"] == 0
    assert features["excess_reflections"] == 3
    assert features["num_excess_reflection_beams"] == 2
    assert features["num_beam_edges"] == 11


def test_minimum_blocks_on_path():
    # doesn't need any pieces for this test
    full_board = """
......
......
......
......
......
......
"""
    board = Board.create(full_board=full_board)

    # end on board (in line)
    # ......
    # ......
    # s..e..
    # ......
    # ......
    # ......
    assert minimum_blocks_on_path(board, (0, 2), (3, 2)) == 0

    # end on board (not in line)
    # ......
    # ......
    # s.....
    # ......
    # ...e..
    # ......
    assert minimum_blocks_on_path(board, (0, 2), (3, 4)) == 1

    # same edge
    # ......
    # ......
    # s.....
    # e.....
    # ......
    # ......
    assert minimum_blocks_on_path(board, (0, 2), (0, 3)) == 2

    # adjacent edges
    # ......
    # ......
    # s.....
    # ......
    # ......
    # ...e..
    assert minimum_blocks_on_path(board, (0, 2), (3, 5)) == 1

    # adjacent edges (another case)
    # ...e..
    # ......
    # s.....
    # ......
    # ......
    # ......
    assert minimum_blocks_on_path(board, (0, 2), (3, 0)) == 1

    # opposite (in line)
    # ......
    # ......
    # s....e
    # ......
    # ......
    # ......
    assert minimum_blocks_on_path(board, (0, 2), (5, 2)) == 0

    # opposite (not in line)
    # ......
    # .....e
    # s.....
    # ......
    # ......
    # ......
    assert minimum_blocks_on_path(board, (0, 2), (5, 1)) == 2
