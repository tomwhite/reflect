import itertools
from itertools import chain, combinations

import numba as nb
import numpy as np

from reflect.board import Board, block_int_to_str_array
from reflect.count import (
    decode_board,
    encode_beams_from_puzzle,
    encode_beams_from_puzzle_with_balls,
    encode_pieces_from_ints,
    load_all_puzzles,
)
from reflect.util import cproduct_idx

# TODO: do this lazily?
num_pieces_to_puzzles = load_all_puzzles("puzzles.bin")


# from https://docs.python.org/3/library/itertools.html#itertools-recipes
def powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


def solve(puzzle, *, fewer_pieces_allowed=False, ball_on_two_ended_beam_allowed=False):
    """Brute force search for all solutions to a puzzle.

    Useful for a setter to see if a puzzle has a unique solution.

    Parameters
    ----------
    puzzle : Puzzle
        A puzzle object.
    fewer_pieces_allowed : bool, optional
        If True, allow solutions that use fewer pieces.
    ball_on_two_ended_beam_allowed : bool, optional
        If True, allow solutions where a ball blocks a two-ended beam
    """
    beams = puzzle.beams
    pieces = puzzle.pieces_ints
    solution_boards = []
    if fewer_pieces_allowed:
        # `pieces` is a multiset so wrap in a set to remove duplicates
        pieces_subsets = set(powerset(pieces))
    else:
        pieces_subsets = [pieces]
    for pieces_subset in pieces_subsets:
        permutations = piece_permutations(pieces_subset)
        solutions = _solve(beams, permutations, ball_on_two_ended_beam_allowed)
        for solution in solutions:
            full_board = puzzle.values.copy()  # contains beam letters on edge
            full_board[1 : puzzle.n + 1, 1 : puzzle.n + 1] = block_int_to_str_array(
                solution
            )
            solution_board = Board.create(full_board=full_board)
            solution_boards.append(solution_board)
    return solution_boards


def has_unique_solution(
    board, *, fewer_pieces_allowed=False, ball_on_two_ended_beam_allowed=False
):
    return (
        len(
            solve(
                board,
                fewer_pieces_allowed=fewer_pieces_allowed,
                ball_on_two_ended_beam_allowed=ball_on_two_ended_beam_allowed,
            )
        )
        == 1
    )


def piece_permutations(pieces):
    """Find the unique permutations for a multi-set (list) of block pieces, represented as integers."""
    permutations = set(
        itertools.permutations(pieces)
    )  # convert to a set for uniqueness
    return np.array(list(permutations), dtype=np.int8)


@nb.njit(nb.boolean(nb.int8[:, :], nb.int8[:, :], nb.boolean), cache=True)
def is_solution(
    beams, hidden_blocks, ball_on_two_ended_beam_allowed
):  # pragma: no cover
    # beams is a array of shape (m, 4), where m is the number of beams
    # columns are: start x, start y, end x, end y
    # hidden_blocks is an (n, n) array
    m = beams.shape[0]
    n = hidden_blocks.shape[0]
    max_j = 2 if ball_on_two_ended_beam_allowed else 1
    for i in range(m):
        for j in range(max_j):
            if j == 0:
                x = beams[i, 0]
                y = beams[i, 1]
                end_x = beams[i, 2]
                end_y = beams[i, 3]
            else:
                x = beams[i, 2]
                y = beams[i, 3]
                end_x = beams[i, 0]
                end_y = beams[i, 1]
            if x == -1:
                dx, dy = 1, 0
            elif x == n:
                dx, dy = -1, 0
            elif y == -1:
                dx, dy = 0, 1
            elif y == n:
                dx, dy = 0, -1
            x, y = x + dx, y + dy
            # update x, y until we fall off board, and check if it's at end_x, end_y
            while True:
                if x == -1 or x == n or y == -1 or y == n:
                    if x != end_x or y != end_y:
                        return False
                    break  # next beam
                val = hidden_blocks[y, x]
                if val == 1:  # /
                    dx, dy = -dy, -dx
                elif val == 2:  # \
                    dx, dy = dy, dx
                elif val == 3:  # o
                    if ball_on_two_ended_beam_allowed:
                        # we know it's reflected back to start
                        break  # next beam
                    else:
                        dx, dy = -dx, -dy
                x, y = x + dx, y + dy
    return True


@nb.njit(nb.int8[:, :, :](nb.int8[:, :], nb.int8[:, :], nb.boolean), cache=True)
def _solve(beams, permutations, ball_on_two_ended_beam_allowed):  # pragma: no cover
    solutions = np.zeros((10, 4, 4), dtype=np.int8)  # first 10 solutions only
    num_solutions = 0
    hidden_blocks = np.zeros(16, dtype=np.int8)
    hidden_blocks_square = hidden_blocks.reshape((4, 4))
    num_permutations = permutations.shape[0]
    length = permutations.shape[1]
    sizes = np.asarray([16] * length, dtype=np.int32)
    tuples = cproduct_idx(sizes)

    for i in range(len(tuples)):
        for p in range(num_permutations):
            # set blocks for this tuple/permutation
            for j in range(length):
                hidden_blocks[tuples[i, j]] = permutations[p][j]

            # test if these blocks form a solution
            if is_solution(beams, hidden_blocks_square, ball_on_two_ended_beam_allowed):
                if num_solutions < len(solutions):
                    solutions[num_solutions] = hidden_blocks_square.copy()
                num_solutions += 1

        # reset hidden_blocks back to zero before moving on to next tuple
        for j in range(length):
            hidden_blocks[tuples[i, j]] = 0

    if num_solutions < len(solutions):
        solutions = solutions[:num_solutions]
    # return num_solutions, solutions # TODO: how to do this in numba
    return solutions


# The "quick" solve functions use the code from count.py which pre-compute all boards
# of a certain size. Solving a board is then essentially a question of doing a
# lookup in the set of all boards given some constraints on pieces and beams.


def _get_all_puzzles(num_pieces, fewer_pieces_allowed=False):
    if not fewer_pieces_allowed:
        return num_pieces_to_puzzles[num_pieces]

    # concat all arrays for all puzzles up to num_pieces
    all_boards_list = []
    all_beams_list = []
    all_pieces_list = []
    for n in range(num_pieces + 1):
        _, all_boards, all_beams, all_pieces = num_pieces_to_puzzles[n]
        all_boards_list.append(all_boards)
        all_beams_list.append(all_beams)
        all_pieces_list.append(all_pieces)

    all_boards = np.concatenate(all_boards_list)
    all_beams = np.concatenate(all_beams_list)
    all_pieces = np.concatenate(all_pieces_list)

    return None, all_boards, all_beams, all_pieces


def _boards_and_beams_for_pieces(puzzle, *, fewer_pieces_allowed=False):
    num_pieces = len(puzzle.pieces)

    _, all_boards, all_beams, all_pieces = _get_all_puzzles(
        num_pieces, fewer_pieces_allowed=fewer_pieces_allowed
    )

    if not fewer_pieces_allowed:
        # simple case: use exactly num_pieces
        pieces_val = encode_pieces_from_ints(puzzle.pieces_ints)
        pieces_index = all_pieces == pieces_val

    else:
        # use num_pieces or fewer
        pieces_subsets = set(powerset(puzzle.pieces_ints))
        pieces_vals = np.empty(len(pieces_subsets), dtype=np.uint32)
        for i, pieces_subset in enumerate(pieces_subsets):
            pieces_ints_subset = np.array(list(pieces_subset), dtype=np.int8)
            pieces_vals[i] = encode_pieces_from_ints(pieces_ints_subset)
        pieces_index = np.isin(all_pieces, pieces_vals)

    # restrict to boards and beams with desired pieces
    boards_with_pieces = all_boards[pieces_index]
    beams_with_pieces = all_beams[pieces_index]

    return boards_with_pieces, beams_with_pieces


def _boards_for_beams(
    puzzle,
    boards_with_pieces,
    beams_with_pieces,
    *,
    ball_on_two_ended_beam_allowed=False
):
    if not ball_on_two_ended_beam_allowed:
        # simple case: use exact beams from puzzle
        beams_val, beams_mask = encode_beams_from_puzzle(puzzle)
        beams_index = (beams_with_pieces & beams_mask) == beams_val
    else:
        # allow multiple sets of beams
        beams_vals, beams_mask = encode_beams_from_puzzle_with_balls(puzzle)
        beams_index = np.isin(beams_with_pieces & beams_mask, beams_vals)

    # restrict to boards with desired beams
    matching_boards = boards_with_pieces[beams_index]

    return matching_boards


def _create_solution_board(puzzle, board):
    # fills in beam letters
    full_board = puzzle.values.copy()  # contains beam letters on edge
    full_board[1 : puzzle.n + 1, 1 : puzzle.n + 1] = board.hidden_blocks
    return Board.create(full_board=full_board)


def _quick_solve(
    puzzle, *, fewer_pieces_allowed=False, ball_on_two_ended_beam_allowed=False
):
    # restrict to boards and beams with desired pieces
    boards_with_pieces, beams_with_pieces = _boards_and_beams_for_pieces(
        puzzle, fewer_pieces_allowed=fewer_pieces_allowed
    )

    # restrict to beams in puzzle
    matching_boards = _boards_for_beams(
        puzzle,
        boards_with_pieces,
        beams_with_pieces,
        ball_on_two_ended_beam_allowed=ball_on_two_ended_beam_allowed,
    )

    return matching_boards


def quick_solve(
    puzzle, *, fewer_pieces_allowed=False, ball_on_two_ended_beam_allowed=False
):
    matching_boards = _quick_solve(
        puzzle,
        fewer_pieces_allowed=fewer_pieces_allowed,
        ball_on_two_ended_beam_allowed=ball_on_two_ended_beam_allowed,
    )
    return [_create_solution_board(puzzle, decode_board(b)) for b in matching_boards]


def quick_count_solutions(puzzle, *, fewer_pieces_allowed=False):
    matching_boards = _quick_solve(puzzle, fewer_pieces_allowed=fewer_pieces_allowed)
    return len(matching_boards)


def quick_has_unique_solution(board, *, fewer_pieces_allowed=False):
    return quick_count_solutions(board, fewer_pieces_allowed=fewer_pieces_allowed) == 1
