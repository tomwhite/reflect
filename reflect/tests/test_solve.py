import numpy as np
from numpy.testing import assert_array_equal

from reflect import cproduct_idx, is_solution, piece_permutations, solve


def test_piece_permutations():
    pieces = [1, 1, 2]
    permutations = piece_permutations(pieces)
    # convert to set to avoid order differences
    s = set(tuple(a) for a in permutations.tolist())
    assert_array_equal(s, set([(1, 1, 2), (1, 2, 1), (2, 1, 1)]))

    pieces = [1, 2, 3]
    permutations = piece_permutations(pieces)
    s = set(tuple(a) for a in permutations.tolist())
    assert_array_equal(
        s, set([(1, 2, 3), (1, 3, 2), (2, 1, 3), (2, 3, 1), (3, 1, 2), (3, 2, 1)])
    )


def test_cproduct_idx():
    sizes = np.asarray([3, 3], dtype=np.int32)
    tuples = cproduct_idx(sizes)
    assert_array_equal(tuples, [[0, 1], [0, 2], [1, 2]])


def test_is_solution():
    # same as test_full_board
    beams = np.array(
        [
            [3, -1, 4, 2],
            [-1, 3, 4, 3],
            [2, 4, 3, 4],
        ],
        dtype=np.int8,
    )
    hidden_blocks = np.array(
        [
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 1, 2],
            [0, 0, 0, 0],
        ],
        dtype=np.int8,
    )
    assert is_solution(beams, hidden_blocks)
    assert not is_solution(beams, np.zeros((4, 4), dtype=np.int8))


def test_solve():
    beams = np.array(
        [
            [3, -1, 4, 2],
            [-1, 3, 4, 3],
            [2, 4, 3, 4],
        ],
        dtype=np.int8,
    )
    pieces = [1, 2]
    solutions = solve(beams, pieces)
    solution = np.array(
        [
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 1, 2],
            [0, 0, 0, 0],
        ],
        dtype=np.int8,
    )
    assert_array_equal(solution, solutions[0])
