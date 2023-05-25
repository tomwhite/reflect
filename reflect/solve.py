import itertools
from itertools import chain, combinations

import numba as nb
import numpy as np

from reflect.board import Board, block_int_to_str_array


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


# adapted from https://stackoverflow.com/a/64234230
@nb.njit(nb.int32[:, :](nb.int32[:]), cache=True)
def cproduct_idx(sizes: np.ndarray):  # pragma: no cover
    """Generates ids tuples for a cartesian product"""
    # assert len(sizes) >= 2  # restriction not needed
    tuples_count = np.prod(sizes)
    tuples = np.zeros((tuples_count, len(sizes)), dtype=np.int32)
    tuple_idx = 0
    tuple_idx_max = 0
    # stores the current combination
    current_tuple = np.zeros(len(sizes))
    while tuple_idx < tuples_count:
        # only include strictly increasing tuples
        j = 1
        for i in range(0, len(sizes) - 1):
            if current_tuple[i] >= current_tuple[i + 1]:
                j = 0
                break
        if j == 1:
            tuples[tuple_idx_max] = current_tuple
            tuple_idx_max += 1

        current_tuple[0] += 1
        for i in range(0, len(sizes) - 1):
            if current_tuple[i] == sizes[i]:
                # the reset to 0 and subsequent increment amount to carrying
                # the number to the higher "power"
                current_tuple[i + 1] += 1
                current_tuple[i] = 0
            else:
                break
        tuple_idx += 1
    return tuples[:tuple_idx_max]  # only return ones actually stored


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
