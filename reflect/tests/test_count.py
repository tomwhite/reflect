import pytest
from numpy.testing import assert_array_equal

from reflect import Board
from reflect.count import (
    all_puzzles,
    beam_end_pos,
    canonical_boards,
    canonical_puzzles_with_unique_solution,
    canonicalize_board,
    canonicalize_puzzle,
    compute_and_save_all_puzzles,
    decode_board,
    encode_beams,
    encode_beams_from_board,
    encode_board,
    encode_pieces,
    load_all_puzzles,
    reflect_beams_horizontally,
    reflect_beams_vertically,
    reflect_horizontally,
    reflect_pieces_horizontally,
    reflect_pieces_vertically,
    reflect_vertically,
    transforms,
    transpose,
    transpose_beams,
    transpose_pieces,
)

# This looks a bit like an "F", which is helpful for visualizing transforms
BLOCKS = """
.//\\
./..
.oo.
.\\..
"""


@pytest.fixture
def board():
    return Board.create(hidden_blocks=BLOCKS)


def test_encode_decode_board(board):
    val = encode_board(board)
    assert val == 0b_00010110_00010000_00111100_00100000

    decoded_board = decode_board(val)
    assert_array_equal(decoded_board.hidden_blocks_ints, board.hidden_blocks_ints)


def test_reflect_horizontally(board):
    val = encode_board(board)
    transformed_val = reflect_horizontally(val)
    transformed_board = decode_board(transformed_val)
    assert_array_equal(
        transformed_board.hidden_blocks_ints,
        board.rot90().transpose().hidden_blocks_ints,
    )


def test_reflect_vertically(board):
    val = encode_board(board)
    transformed_val = reflect_vertically(val)
    transformed_board = decode_board(transformed_val)
    assert_array_equal(
        transformed_board.hidden_blocks_ints,
        board.transpose().rot90().hidden_blocks_ints,
    )


def test_transpose(board):
    val = encode_board(board)
    transformed_val = transpose(val)
    transformed_board = decode_board(transformed_val)
    assert_array_equal(
        transformed_board.hidden_blocks_ints, board.transpose().hidden_blocks_ints
    )


def test_transforms(board):
    val = encode_board(board)
    for tb, tv in zip(board.transforms(), transforms(val)):
        assert_array_equal(decode_board(tv).hidden_blocks_ints, tb.hidden_blocks_ints)


def test_canonicalize_board(board):
    val = encode_board(board)
    assert canonicalize_board(val) in transforms(val)


def test_canonical_boards():
    assert len(canonical_boards(num_pieces=1)) == 9


def test_beam_end_pos():
    board_val = 0  # empty
    assert beam_end_pos(board_val, 0x0) == 0xB
    assert beam_end_pos(board_val, 0x1) == 0xA
    assert beam_end_pos(board_val, 0x2) == 0x9
    assert beam_end_pos(board_val, 0x3) == 0x8
    assert beam_end_pos(board_val, 0x4) == 0xF
    assert beam_end_pos(board_val, 0x5) == 0xE
    assert beam_end_pos(board_val, 0x6) == 0xD
    assert beam_end_pos(board_val, 0x7) == 0xC
    assert beam_end_pos(board_val, 0x8) == 0x3
    assert beam_end_pos(board_val, 0x9) == 0x2
    assert beam_end_pos(board_val, 0xA) == 0x1
    assert beam_end_pos(board_val, 0xB) == 0x0
    assert beam_end_pos(board_val, 0xC) == 0x7
    assert beam_end_pos(board_val, 0xD) == 0x6
    assert beam_end_pos(board_val, 0xE) == 0x5
    assert beam_end_pos(board_val, 0xF) == 0x4


def test_encode_beams():
    full_board = """
.EFBH.
A....A
B../.H
C..\\/G
D....D
.EFCG.
"""
    board = Board.create(full_board=full_board)

    #  FEDC
    # 0....B
    # 1../.A
    # 2..\/9
    # 3....8
    #  4567

    # 0 -> B
    # 1 -> D
    # 2 -> 6
    # 3 -> 8
    # 4 -> F
    # 5 -> E
    # 6 -> 2
    # 7 -> 9
    # 8 -> 3
    # 9 -> 7
    # A -> C
    # B -> 0
    # C -> A
    # D -> 1
    # E -> 5
    # F -> 4

    val = encode_beams_from_board(board)
    assert val == 0x_BD68_FE29_37C0_A154

    val2 = encode_beams(encode_board(board))
    assert val2 == val


def test_reflect_beams_horizontally(board):
    val = encode_beams(encode_board(board))
    assert reflect_beams_horizontally(val) == encode_beams(
        reflect_horizontally(encode_board(board))
    )


def test_reflect_beams_vertically(board):
    val = encode_beams(encode_board(board))
    assert reflect_beams_vertically(val) == encode_beams(
        reflect_vertically(encode_board(board))
    )


def test_transpose_beams(board):
    val = encode_beams(encode_board(board))
    assert transpose_beams(val) == encode_beams(transpose(encode_board(board)))


def test_encode_pieces(board):
    val = encode_pieces(encode_board(board))
    assert val == 0x223  # 2 o, 2 \, 3 /


def test_reflect_pieces_horizontally(board):
    val = encode_pieces(encode_board(board))
    assert reflect_pieces_horizontally(val) == encode_pieces(
        reflect_horizontally(encode_board(board))
    )


def test_reflect_pieces_vertically(board):
    val = encode_pieces(encode_board(board))
    assert reflect_pieces_vertically(val) == encode_pieces(
        reflect_vertically(encode_board(board))
    )


def test_transpose_pieces(board):
    val = encode_pieces(encode_board(board))
    assert transpose_pieces(val) == encode_pieces(transpose(encode_board(board)))


def test_canonicalize_puzzle():
    blocks1 = """
....
../.
..\\/
....
"""
    board1 = Board.create(hidden_blocks=blocks1)

    blocks2 = """
....
../\\
.../
....
"""
    board2 = Board.create(hidden_blocks=blocks2)

    # the boards are distinct...
    canonical_board1_val = canonicalize_board(encode_board(board1))
    canonical_board2_val = canonicalize_board(encode_board(board2))
    assert canonical_board1_val != canonical_board2_val

    beams1 = encode_beams(canonical_board1_val)
    beams2 = encode_beams(canonical_board2_val)

    pieces1 = encode_pieces(canonical_board1_val)
    pieces2 = encode_pieces(canonical_board2_val)

    # ... but the puzzles resulting from them are not
    # (in other words, the puzzle doesn't have a unique solution)
    assert canonicalize_puzzle(beams1, pieces1) == canonicalize_puzzle(beams2, pieces2)


def test_canonical_puzzles_with_unique_solution():
    canonical_beams, canonical_pieces = canonical_puzzles_with_unique_solution(
        num_pieces=1
    )
    assert len(canonical_beams) == len(canonical_pieces)
    assert len(canonical_beams) == 9

    canonical_beams, canonical_pieces = canonical_puzzles_with_unique_solution(
        num_pieces=2
    )
    assert len(canonical_beams) == len(canonical_pieces)
    assert len(canonical_beams) == 149  # TODO: can we check this?


@pytest.mark.skip()
def test_number_canonical_puzzles_with_unique_solution():
    for num_pieces in range(1, 8):
        canonical_beams, canonical_pieces = canonical_puzzles_with_unique_solution(
            num_pieces=num_pieces
        )
        assert len(canonical_beams) == len(canonical_pieces)
        print(num_pieces, len(canonical_beams))


def test_load_and_save_puzzles(tmp_path):
    filename = tmp_path / "puzzles.bin"
    compute_and_save_all_puzzles(max_pieces=3, filename=filename)
    num_pieces_to_puzzles = load_all_puzzles(filename)

    duplicate_groups, all_boards, all_beams, all_pieces = num_pieces_to_puzzles[3]
    exp_duplicate_groups, exp_all_boards, exp_all_beams, exp_all_pieces = all_puzzles(3)

    assert_array_equal(duplicate_groups, exp_duplicate_groups)
    assert_array_equal(all_boards, exp_all_boards)
    assert_array_equal(all_beams, exp_all_beams)
    assert_array_equal(all_pieces, exp_all_pieces)
