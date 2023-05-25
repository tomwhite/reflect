import numpy as np
from numpy.testing import assert_array_equal

from reflect import Board, Puzzle, cproduct_idx, is_solution, piece_permutations, solve


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
    assert is_solution(beams, hidden_blocks, False)
    assert not is_solution(beams, np.zeros((4, 4), dtype=np.int8), False)


def test_solve():
    values = """
....A.
......
......
.....A
B....B
...CC.
"""
    pieces = ["/", "\\"]
    puzzle = Puzzle.create(values, pieces)
    solutions = solve(puzzle)
    assert len(solutions) == 1

    expected_solution = """
....A.
......
......
.../\\A
B....B
...CC.
"""
    board = Board.create(full_board=expected_solution)
    assert solutions[0].puzzle_solution() == board.puzzle_solution()


def test_solve__fewer_pieces_allowed():
    # set on 2023-04-14
    values = """
.ABCD.
B....E
E.....
F....F
A.....
.GHID.
"""
    pieces = ["/", "/", "/", "\\", "o", "o"]
    puzzle = Puzzle.create(values, pieces)

    solutions = solve(puzzle)
    assert len(solutions) == 1

    expected_solution = """
.ABCD.
B./..E
E./o..
F....F
A/o\\..
.GHID.
"""
    board = Board.create(full_board=expected_solution)
    assert solutions[0].puzzle_solution() == board.puzzle_solution()

    # first three don't use a \ piece
    expected_solutions = set(
        [
            """.ABCD.
B./..E
E./o..
F....F
A/o...
.GHID.""",
            """.ABCD.
B./..E
E./o..
F....F
A/.o..
.GHID.""",
            """.ABCD.
B./..E
E./...
F....F
A/oo..
.GHID.""",
            """.ABCD.
B./..E
E./o..
F....F
A/o\\..
.GHID.""",
        ]
    )

    solutions = solve(puzzle, fewer_pieces_allowed=True)
    assert len(solutions) == 4
    assert (
        set(solution.puzzle_solution() for solution in solutions) == expected_solutions
    )


def test_solve__ball_on_two_ended_beam_allowed():
    # set on 2023-04-16
    values = """
.AA.C.
D....I
D....G
.....J
.....C
.G..I.
"""
    pieces = ["/", "/", "/", "\\", "\\", "o"]
    puzzle = Puzzle.create(values, pieces)

    solutions = solve(puzzle)
    assert len(solutions) == 1

    expected_solution = """
.AA.C.
D\\/./I
D/...G
...o.J
..\\..C
.G..I.
"""
    board = Board.create(full_board=expected_solution)
    assert solutions[0].puzzle_solution() == board.puzzle_solution()

    # first three have a 'o' piece blocking a two-ended beam
    expected_solutions = set(
        [
            """.AA.C.
D\\/./I
D/...G
.o...J
..\\..C
.G..I.""",
            """.AA.C.
D\\/./I
D/...G
..o..J
..\\..C
.G..I.""",
            """.AA.C.
D\\/./I
D/...G
....oJ
..\\..C
.G..I.""",
            """.AA.C.
D\\/./I
D/...G
...o.J
..\\..C
.G..I.""",
        ]
    )

    solutions = solve(puzzle, ball_on_two_ended_beam_allowed=True)
    assert len(solutions) == 4
    assert (
        set(solution.puzzle_solution() for solution in solutions) == expected_solutions
    )
