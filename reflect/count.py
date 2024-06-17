import itertools
import pickle

import numba as nb
import numpy as np

from reflect.board import Board, block_int_to_str_array
from reflect.util import cproduct_idx


def encode_board(board):
    """Encode a board as an unsigned int by packing bits.
    One piece is represented in a pair of bits.
    """
    assert board.n == 4
    shift = 15 * 2
    val = 0
    # cast to int64 so that val has same type
    block_ints = board.hidden_blocks_ints.astype(np.int64)
    for i in range(4):
        for j in range(4):
            val |= block_ints[i, j] << shift
            shift -= 2
    return val


def decode_board(val):
    """Decode an unsigned int value to a board by unpacking bits."""
    shift = 15 * 2
    blocks = np.zeros((4, 4), dtype=np.int8)
    for i in range(4):
        for j in range(4):
            blocks[i, j] = val >> shift & 0b11
            shift -= 2
    return Board.create(hidden_blocks=block_int_to_str_array(blocks))


@nb.njit(nb.uint32(nb.uint32), cache=True)
def reflect_horizontally(val):
    """Reflect the encoded board horizontally"""

    # Note that we reflect each bit, not a pair of bits,
    # since each piece is reflected too:
    #
    # / = 0b01 -> \ = 0b10
    # \ = 0b10 -> / = 0b01
    # o = 0b11 -> o = 0b11

    c1 = val & 0b_10000000_10000000_10000000_10000000
    c2 = val & 0b_01000000_01000000_01000000_01000000
    c3 = val & 0b_00100000_00100000_00100000_00100000
    c4 = val & 0b_00010000_00010000_00010000_00010000
    c5 = val & 0b_00001000_00001000_00001000_00001000
    c6 = val & 0b_00000100_00000100_00000100_00000100
    c7 = val & 0b_00000010_00000010_00000010_00000010
    c8 = val & 0b_00000001_00000001_00000001_00000001

    return (
        (c1 >> 7)
        | (c2 >> 5)
        | (c3 >> 3)
        | (c4 >> 1)
        | (c5 << 1)
        | (c6 << 3)
        | (c7 << 5)
        | (c8 << 7)
    )


@nb.njit(nb.uint32(nb.uint32), cache=True)
def reflect_vertically(val):
    """Reflect the encoded board vertically"""

    # pieces are reflected like in reflect_horizontally

    r1 = val & 0b_10101010_00000000_00000000_00000000
    r2 = val & 0b_01010101_00000000_00000000_00000000
    r3 = val & 0b_00000000_10101010_00000000_00000000
    r4 = val & 0b_00000000_01010101_00000000_00000000
    r5 = val & 0b_00000000_00000000_10101010_00000000
    r6 = val & 0b_00000000_00000000_01010101_00000000
    r7 = val & 0b_00000000_00000000_00000000_10101010
    r8 = val & 0b_00000000_00000000_00000000_01010101

    return (
        (r1 >> 25)
        | (r2 >> 23)
        | (r3 >> 9)
        | (r4 >> 7)
        | (r5 << 7)
        | (r6 << 9)
        | (r7 << 23)
        | (r8 << 25)
    )


@nb.njit(nb.uint32(nb.uint32), cache=True)
def transpose(val):
    """Reflect the encoded board in y=x"""

    # pieces are *not* reflected

    # Based on https://github.com/jdleesmiller/twenty48/blob/479f646e81c38f1967e4fc5942617f9650d2c735/ext/twenty48/state.hpp#L191-L198

    # First move cells as follows (D = leave, L = 3 left, R = 3 right)
    #
    # [D R D R]
    # [L D L D]
    # [D R D R]
    # [L D L D]
    #
    # Consider the following example, where numbers are cell labels (not values in the array):
    #
    # [ 0  1  2  3]      [ 0  4  2  6]
    # [ 4  5  6  7]  ->  [ 1  5  3  7]
    # [ 8  9 10 11]      [ 8 12 10 14]
    # [12 13 14 15]      [ 9 13 11 15]

    a1 = val & 0b_11001100_00110011_11001100_00110011  # diagonal
    a2 = val & 0b_00000000_11001100_00000000_11001100  # move 3 left
    a3 = val & 0b_00110011_00000000_00110011_00000000  # move 3 right
    a = a1 | (a2 << 6) | (a3 >> 6)

    # Then move cells as follows (D = leave, L = 6 left, R = 6 right)
    #
    # [D D R R]
    # [D D R R]
    # [L L D D]
    # [L L D D]
    #
    # Continuing the example:
    #
    # [ 0  4  2  6]      [ 0  4  8 12]
    # [ 1  5  3  7]  ->  [ 1  5  9 13]
    # [ 8 12 10 14]      [ 2  6 10 14]
    # [ 9 13 11 15]      [ 3  7 11 15]
    #
    # which is the transposed array.

    b1 = a & 0b_11110000_11110000_00001111_00001111  # diagonal
    b2 = a & 0b_00000000_00000000_11110000_11110000  # move 6 left
    b3 = a & 0b_00001111_00001111_00000000_00000000  # move 6 right

    return b1 | (b2 << 12) | (b3 >> 12)


@nb.njit(nb.uint32[:](nb.uint32), cache=True)
def transforms(val):
    """Return all the transforms of the encoded board."""
    horizontal_reflection = reflect_horizontally(val)
    vertical_reflection = reflect_vertically(val)
    transposition = transpose(val)

    rotated_90 = reflect_horizontally(transposition)
    rotated_180 = reflect_vertically(horizontal_reflection)
    rotated_270 = reflect_vertically(transposition)

    anti_transposition = reflect_vertically(rotated_90)

    # the order doesn't really matter, but match board.transforms()
    return np.array(
        [
            val,
            rotated_270,
            rotated_180,
            rotated_90,
            transposition,
            vertical_reflection,
            anti_transposition,
            horizontal_reflection,
        ],
        dtype=np.uint32,
    )


@nb.njit(nb.uint32(nb.uint32), cache=True)
def canonicalize_board(val):
    """Return the canonical encoded board from the set of transforms of the given board."""

    # don't call transforms here to avoid allocating an array
    horizontal_reflection = reflect_horizontally(val)
    vertical_reflection = reflect_vertically(val)
    transposition = transpose(val)

    rotated_90 = reflect_horizontally(transposition)
    rotated_180 = reflect_vertically(horizontal_reflection)
    rotated_270 = reflect_vertically(transposition)

    anti_transposition = reflect_vertically(rotated_90)

    return min(
        val,
        rotated_270,
        rotated_180,
        rotated_90,
        transposition,
        vertical_reflection,
        anti_transposition,
        horizontal_reflection,
    )


def all_boards(num_pieces):
    """Return an array containing all the boards containing `num_pieces`."""
    product = itertools.product([1, 2, 3], repeat=num_pieces)
    selections = np.array(list(product), dtype=np.int8)
    return _all_boards(selections)


@nb.njit(nb.uint32[:](nb.int8[:, :]), cache=True)
def _all_boards(selections):
    num_selections = selections.shape[0]
    length = selections.shape[1]
    sizes = np.asarray([16] * length, dtype=np.int32)
    tuples = cproduct_idx(sizes)

    boards = np.empty(len(tuples) * num_selections, dtype=np.uint32)

    for i in range(len(tuples)):
        for p in range(num_selections):
            val = 0
            # set blocks for this tuple/selection
            for j in range(length):
                val |= selections[p][j] << (tuples[i, j] * 2)
            boards[i * num_selections + p] = val

    return boards


def canonical_boards(num_pieces):
    """Return an array containing all the canonical boards containing `num_pieces`."""
    product = itertools.product([1, 2, 3], repeat=num_pieces)
    selections = np.array(list(product), dtype=np.int8)
    return _canonical_boards(selections)


@nb.njit(nb.uint32[:](nb.int8[:, :]), cache=True)
def _canonical_boards(selections):
    num_selections = selections.shape[0]
    length = selections.shape[1]
    sizes = np.asarray([16] * length, dtype=np.int32)
    tuples = cproduct_idx(sizes)

    boards = np.empty(len(tuples) * num_selections, dtype=np.uint32)

    for i in range(len(tuples)):
        for p in range(num_selections):
            val = 0
            # set blocks for this tuple/selection
            for j in range(length):
                val |= selections[p][j] << (tuples[i, j] * 2)
            boards[i * num_selections + p] = canonicalize_board(val)

    return np.unique(boards)


@nb.njit(nb.uint64(nb.uint64, nb.int32), cache=True)
def beam_end_pos(board_val, start_pos):

    # FEDC
    # BA98
    # 7654
    # 3210

    # directions
    UP = 4
    DOWN = -4
    LEFT = 1
    RIGHT = -1

    # initialize
    if start_pos <= 3:
        off = (3 - start_pos) * 4 + 3
        dir = RIGHT
    elif start_pos >= 0x4 and start_pos <= 0x7:
        off = 7 - start_pos
        dir = UP
    elif start_pos >= 0x8 and start_pos <= 0xB:
        off = (start_pos - 8) * 4
        dir = LEFT
    elif start_pos >= 0xC:
        off = start_pos
        dir = DOWN

    while True:

        # reflect
        block = (board_val >> (off * 2)) & 0b11
        if block == 1:  # /
            if dir == UP:
                dir = RIGHT
            elif dir == DOWN:
                dir = LEFT
            elif dir == LEFT:
                dir = DOWN
            elif dir == RIGHT:
                dir = UP
        elif block == 2:  # \
            if dir == UP:
                dir = LEFT
            elif dir == DOWN:
                dir = RIGHT
            elif dir == LEFT:
                dir = UP
            elif dir == RIGHT:
                dir = DOWN
        elif block == 3:  # o
            dir = -dir

        # detect edge
        if dir == RIGHT and off % 4 == 0:
            return off // 4 + 8
        elif dir == LEFT and off % 4 == 3:
            return 3 - off // 4
        elif dir == UP and off >= 0xC:
            return off
        elif dir == DOWN and off <= 3:
            return 7 - off

        # move
        off = (off + dir) % 16


@nb.njit(nb.uint64(nb.uint64), cache=True)
def encode_beams(board_val):
    """Encode all beams on an encoded board as an unsigned int by packing bits.
    Each beam is four bits indicating the end edge position.

    Positions are numbered as follows:

    ```
      FEDC
     0....B
     1....A
     2....9
     3....8
      4567
    ```
    """
    shift = 15 * 4
    val = 0
    for start_pos in range(16):
        end_pos = beam_end_pos(board_val, start_pos)
        val |= end_pos << shift
        shift -= 4
    return val


def encode_beams_from_board(board):
    # equivalent to encode_beams, but from a board object - useful for testing
    assert board.n == 4

    beams = board.beams + 1  # adjust coordinates
    startxy_to_endxy = {}
    for i in range(beams.shape[0]):
        x = beams[i, 0]
        y = beams[i, 1]
        end_x = beams[i, 2]
        end_y = beams[i, 3]
        startxy_to_endxy[(x, y)] = (end_x, end_y)
        startxy_to_endxy[(end_x, end_y)] = (x, y)

    ind_to_xy = {}
    xy_to_ind = {}
    for i, (x, y) in enumerate(board.edge_locations_alt()):
        ind_to_xy[i] = (x, y)
        xy_to_ind[(x, y)] = i

    shift = 15 * 4
    val = 0
    for i, (x, y) in ind_to_xy.items():
        ind = xy_to_ind[startxy_to_endxy[(x, y)]]
        val |= ind << shift
        shift -= 4
    return val


def encode_beams_from_puzzle(puzzle):
    """Encode beams for a puzzle, which typically has less than
    all possible beams for a board.

    This works like `encode_beams` but also returns a bit mask
    to indicate which beams are encoded.
    """
    assert puzzle.n == 4

    beams = puzzle.beams + 1  # adjust coordinates
    startxy_to_endxy = {}
    for i in range(beams.shape[0]):
        x = beams[i, 0]
        y = beams[i, 1]
        end_x = beams[i, 2]
        end_y = beams[i, 3]
        startxy_to_endxy[(x, y)] = (end_x, end_y)
        startxy_to_endxy[(end_x, end_y)] = (x, y)

    ind_to_xy = {}
    xy_to_ind = {}
    for i, (x, y) in enumerate(puzzle.edge_locations_alt()):
        ind_to_xy[i] = (x, y)
        xy_to_ind[(x, y)] = i

    shift = 15 * 4
    val = 0
    mask = 0
    for i, (x, y) in ind_to_xy.items():
        if puzzle.values[y, x] == ".":
            mask |= 0b0000 << shift
        else:
            mask |= 0b1111 << shift
            ind = xy_to_ind[startxy_to_endxy[(x, y)]]
            val |= ind << shift
        shift -= 4
    return val, mask


def encode_beams_from_puzzle_with_balls(puzzle):
    # Like encode_beams_from_puzzle but takes mirror balls into account.
    # The idea is to change two-ended beams into two one-ended beams
    # so that we can detect cases where a ball has been placed in the middle
    # of a two-ended beam, for when ball_on_two_ended_beam_allowed is True.
    assert puzzle.n == 4

    beams = puzzle.beams + 1  # adjust coordinates
    num_two_ended_beams = 0
    startxy_to_endxy = {}
    for i in range(beams.shape[0]):
        x = beams[i, 0]
        y = beams[i, 1]
        end_x = beams[i, 2]
        end_y = beams[i, 3]
        startxy_to_endxy[(x, y)] = (end_x, end_y)
        if not (x == end_x and y == end_y):
            num_two_ended_beams += 1
            startxy_to_endxy[(end_x, end_y)] = (x, y)

    ind_to_xy = {}
    xy_to_ind = {}
    for i, (x, y) in enumerate(puzzle.edge_locations_alt()):
        ind_to_xy[i] = (x, y)
        xy_to_ind[(x, y)] = i

    shift = 15 * 4
    val = 0
    mask = 0
    for i, (x, y) in ind_to_xy.items():
        if puzzle.values[y, x] == ".":
            # TODO: has no effect
            mask |= 0b0000 << shift
        else:
            mask |= 0b1111 << shift
            ind = xy_to_ind[startxy_to_endxy[(x, y)]]
            val |= ind << shift
        shift -= 4
    vals = [val]

    # TODO: need to do for all combinations
    shift = 15 * 4
    for i, (x, y) in ind_to_xy.items():
        if puzzle.values[y, x] != ".":
            ind = xy_to_ind[startxy_to_endxy[(x, y)]]
            if ind != i:
                # make pos i and ind both one-ended
                val2 = val
                val2 &= ~(0b1111 << shift)  # reset
                val2 |= i << shift
                ind_shift = (15 - ind) * 4
                val2 &= ~(0b1111 << ind_shift)  # reset
                val2 |= ind << ind_shift
                vals.append(val2)
        shift -= 4

    vals = np.unique(vals)

    return vals, mask


@nb.njit(nb.uint64(nb.uint64), cache=True)
def reflect_beams_horizontally(val):
    """Reflect the encoded beams horizontally"""

    # This transformation changes edge position i to (11 - i) % 16

    r = 0
    for i in range(16):
        shift = (15 - i) * 4
        end = val >> shift & 0xF
        tr_i = (11 - i) % 16
        tr_end = (11 - end) % 16
        tr_shift = (15 - tr_i) * 4
        r |= tr_end << tr_shift
    return r


@nb.njit(nb.uint64(nb.uint64), cache=True)
def reflect_beams_vertically(val):
    """Reflect the encoded beams vertically"""

    # This transformation changes edge position i to (3 - i) % 16

    r = 0
    for i in range(16):
        shift = (15 - i) * 4
        end = val >> shift & 0xF
        tr_i = (3 - i) % 16
        tr_end = (3 - end) % 16
        tr_shift = (15 - tr_i) * 4
        r |= tr_end << tr_shift
    return r


@nb.njit(nb.uint64(nb.uint64), cache=True)
def transpose_beams(val):
    """Reflect the encoded beams in y=x"""

    # This transformation changes edge position i to 15 - i

    r = 0
    for i in range(16):
        shift = (15 - i) * 4
        end = val >> shift & 0xF
        tr_i = 15 - i
        tr_end = 15 - end
        tr_shift = (15 - tr_i) * 4
        r |= tr_end << tr_shift
    return r


@nb.njit(nb.uint64(nb.uint64), cache=True)
def count_beams(val):
    """Count the number of encoded beams"""

    c = 0  # number of positions that reflect back to self
    for i in range(16):
        shift = (15 - i) * 4
        end = val >> shift & 0xF
        if i == end:
            c += 1
    return 8 + (c // 2)


@nb.njit(nb.uint32(nb.uint64), cache=True)
def encode_pieces(board_val):
    """Encode a multiset of pieces from an encoded board as an unsigned int by packing bits.
    Each distinct piece is represented by a 4-bit count.
    """
    r1 = 0  # count of /
    r2 = 0  # count of \
    r3 = 0  # count of o
    for i in range(16):
        r = board_val >> i * 2 & 0b11
        if r == 1:
            r1 += 1
        elif r == 2:
            r2 += 1
        elif r == 3:
            r3 += 1
    return r1 | (r2 << 4) | (r3 << 8)


@nb.njit(nb.uint32(nb.int8[:]), cache=True)
def encode_pieces_from_ints(pieces):
    r1 = np.sum(pieces == 1)  # count of /
    r2 = np.sum(pieces == 2)  # count of \
    r3 = np.sum(pieces == 3)  # count of o
    return r1 | (r2 << 4) | (r3 << 8)


@nb.njit(nb.uint32(nb.uint32), cache=True)
def reflect_pieces_horizontally(val):
    """Reflect the encoded pieces horizontally"""
    r1 = val & 0x000F  # count of /
    r2 = (val & 0x00F0) >> 4  # count of \
    r3 = (val & 0x0F00) >> 8  # count of o
    return r2 | (r1 << 4) | (r3 << 8)  # switch / and \


@nb.njit(nb.uint32(nb.uint32), cache=True)
def reflect_pieces_vertically(val):
    """Reflect the encoded pieces vertically"""
    return reflect_pieces_horizontally(val)


@nb.njit(nb.uint32(nb.uint32), cache=True)
def transpose_pieces(val):
    """Reflect the encoded pieces in y=x"""
    # pieces don't change for this transformation
    return val


@nb.njit(nb.types.Tuple((nb.uint64, nb.uint32))(nb.uint64, nb.uint32), cache=True)
def canonicalize_puzzle(beams, pieces):

    horizontal_reflection = reflect_beams_horizontally(beams)
    vertical_reflection = reflect_beams_vertically(beams)
    transposition = transpose_beams(beams)

    rotated_90 = reflect_beams_horizontally(transposition)
    rotated_180 = reflect_beams_vertically(horizontal_reflection)
    rotated_270 = reflect_beams_vertically(transposition)

    anti_transposition = reflect_beams_vertically(rotated_90)

    transformed_beams = np.array(
        [
            beams,
            rotated_270,
            rotated_180,
            rotated_90,
            transposition,
            vertical_reflection,
            anti_transposition,
            horizontal_reflection,
        ],
        dtype=np.uint64,
    )
    canonical_beams = min(transformed_beams)

    horizontal_reflection = reflect_pieces_horizontally(pieces)
    vertical_reflection = reflect_pieces_vertically(pieces)
    transposition = transpose_pieces(pieces)

    rotated_90 = reflect_pieces_horizontally(transposition)
    rotated_180 = reflect_pieces_vertically(horizontal_reflection)
    rotated_270 = reflect_pieces_vertically(transposition)

    anti_transposition = reflect_pieces_vertically(rotated_90)

    transformed_pieces = np.array(
        [
            pieces,
            rotated_270,
            rotated_180,
            rotated_90,
            transposition,
            vertical_reflection,
            anti_transposition,
            horizontal_reflection,
        ],
        dtype=np.uint32,
    )

    # to restrict transformed beams to all the canonical (minimum) beams in case there are ties
    canonical_pieces = min(transformed_pieces[transformed_beams == canonical_beams])

    return canonical_beams, canonical_pieces


def canonical_puzzles_with_unique_solution(num_pieces):
    """Compute all canonical puzzles with a unique solution containing `num_pieces`, taking symmetries into account."""

    duplicate_groups, _, sorted_beams, sorted_pieces = all_puzzles(num_pieces)

    # remove duplicate groups (non-unique solutions)
    single_solution_beams = sorted_beams[duplicate_groups == 0]
    single_solution_pieces = sorted_pieces[duplicate_groups == 0]

    # canonicalize
    n_puzzles = len(single_solution_beams)
    canonical_beams = np.empty(n_puzzles, dtype=np.uint64)
    canonical_pieces = np.empty(n_puzzles, dtype=np.uint32)
    for i, (beams, pieces) in enumerate(
        zip(single_solution_beams, single_solution_pieces)
    ):
        canonical_beams[i], canonical_pieces[i] = canonicalize_puzzle(beams, pieces)

    # remove duplicate canonical puzzles
    canonical_puzzles = np.stack((canonical_beams, canonical_pieces), axis=1)
    canonical_puzzles = np.unique(canonical_puzzles, axis=0)
    canonical_beams = canonical_puzzles[:, 0]
    canonical_pieces = canonical_puzzles[:, 1].astype(np.uint32)

    return canonical_beams, canonical_pieces


def all_puzzles(num_pieces):
    """Compute all the puzzles containing `num_pieces`.

    Note that symmetries are _not_ taken into account, so puzzles that can be transformed into one another
    will all be returned.
    """
    board_vals = all_boards(num_pieces=num_pieces)
    n_boards = len(board_vals)
    beams_vals = np.empty(n_boards, dtype=np.uint64)
    pieces_vals = np.empty(n_boards, dtype=np.uint32)
    for i, board_val in enumerate(board_vals):
        beams_vals[i] = encode_beams(board_val)
        pieces_vals[i] = encode_pieces(board_val)

    # sort by beams then pieces then board (note that args to lexsort are reversed)
    ind = np.lexsort((board_vals, pieces_vals, beams_vals))
    sorted_boards = board_vals[ind]
    sorted_beams = beams_vals[ind]
    sorted_pieces = pieces_vals[ind]

    # at this point pieces may not be sorted, but we can check for duplicates
    duplicate_groups = np.zeros(n_boards, dtype=np.uint32)
    _, indexes, counts = np.unique(sorted_beams, return_index=True, return_counts=True)

    dup_group_index = 1
    for i in range(len(indexes)):
        if counts[i] > 1:
            index = indexes[i]
            count = counts[i]
            duplicate_pieces = (
                len(np.unique(sorted_pieces[index : index + count])) < count
            )
            if duplicate_pieces:
                duplicate_groups[index : index + count] = dup_group_index
                dup_group_index += 1

    return duplicate_groups, sorted_boards, sorted_beams, sorted_pieces


def compute_and_save_all_puzzles(max_pieces, filename):
    num_pieces_to_puzzles = {}
    for num_pieces in range(max_pieces + 1):
        num_pieces_to_puzzles[num_pieces] = all_puzzles(num_pieces)
    with open(filename, mode="wb") as file:
        pickle.dump(num_pieces_to_puzzles, file)


def load_all_puzzles(filename):
    with open(filename, mode="rb") as file:
        return pickle.load(file)
