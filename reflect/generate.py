import itertools
import random

import numpy as np
from numpy.random import choice, shuffle

from reflect.board import Block, Board
from reflect.count import decode_board, load_all_puzzles
from reflect.solve import _boards_and_beams_for_pieces, _boards_for_beams
from reflect.solve import has_unique_solution as slow_has_unique_solution
from reflect.solve import quick_has_unique_solution


def _match_boards(n_pieces=None, min_pieces=4, max_pieces=7, no_mirror_balls=False):

    if n_pieces is None:
        n_pieces = random.randrange(min_pieces, max_pieces + 1)

    num_pieces_to_puzzles = load_all_puzzles("puzzles.bin")

    duplicate_groups, all_boards, all_beams, all_pieces = num_pieces_to_puzzles[
        n_pieces
    ]

    # remove duplicate groups (non-unique solutions)
    single_solution_boards = all_boards[duplicate_groups == 0]

    # no mirror balls
    if no_mirror_balls:
        single_solution_pieces = all_pieces[duplicate_groups == 0]
        counts_o = (single_solution_pieces & 0xF00) >> 8
        single_solution_boards = single_solution_boards[counts_o == 0]
        single_solution_pieces = single_solution_pieces[counts_o == 0]

    return single_solution_boards


def generate(
    n_pieces=None, min_pieces=4, max_pieces=7, no_mirror_balls=False, debug=False
):
    single_solution_boards = _match_boards(
        n_pieces=n_pieces,
        min_pieces=min_pieces,
        max_pieces=max_pieces,
        no_mirror_balls=no_mirror_balls,
    )

    for _ in range(20):
        if debug:
            print(f"Generating board with {n_pieces} blocks...")

        board = decode_board(choice(single_solution_boards))

        if debug:
            print(board.pieces)

        # turn on all beams
        board.add_all_beams()

        if has_unique_solution(board):
            if debug:
                print("Minimising board...")
            return minimise(board, debug=debug)
        else:
            if debug:
                print("Not unique...")

    # can't generate a board!
    raise ValueError("Failed to generate!")


# TODO: this is no longer used since we have pre-generated all boards
# which we know have unique solutions and can sample at random
def generate_board(n_pieces, debug=False):
    a = choice(
        np.array(
            [
                Block.OBLIQUE_MIRROR.char,
                Block.REVERSE_OBLIQUE_MIRROR.char,
                Block.MIRROR_BALL.char,
            ]
        ),
        p=np.array(
            [
                (n_pieces - 1) / (2 * n_pieces),
                (n_pieces - 1) / (2 * n_pieces),
                1 / n_pieces,
            ]
        ),
        size=n_pieces,
    )
    if debug:
        print(a)
    a = np.concatenate([a, np.full(16 - n_pieces, ".")])
    shuffle(a)
    a = a.reshape(4, 4)
    return Board.create(hidden_blocks=a)


def minimise(board, debug=False):
    # try to remove beams at random while still having a unique solution

    best_board = board
    n_trials = 10

    for i in range(n_trials):
        if debug:
            print(
                f"Trial {i+1} of {n_trials}. Best board has {best_board.num_beams} beams"
            )
        prev_board = board
        while True:
            # find a location with a beam
            edge_locations = list(prev_board.edge_locations())
            while True:
                x, y = random.choice(edge_locations)
                if prev_board.values[y, x] != ".":
                    break
            new_board = prev_board.copy()
            # and remove it
            new_board.remove_beam(x, y)

            # if removing the beam means it is no longer unique
            # then see if the previous (unique) board is the best so far
            if debug:
                print(
                    f"Finding if new board with {new_board.num_beams} beams has unique solution...",
                    end=" ",
                )
            if not has_unique_solution(new_board):
                if debug:
                    print("no")
                if prev_board.num_beams < best_board.num_beams:
                    best_board = prev_board
                break
            else:
                if debug:
                    print("yes")

            prev_board = new_board

    return best_board


def has_unique_solution(board):
    slow_unique = slow_has_unique_solution(
        board, fewer_pieces_allowed=True, ball_on_two_ended_beam_allowed=True
    )
    # ball_on_two_ended_beam_allowed is not supported by quick_has_unique_solution
    # so we can't use it to check uniqueness for boards with a 'o' piece
    if "o" in board.pieces:
        return slow_unique
    quick_unique = quick_has_unique_solution(board, fewer_pieces_allowed=True)
    if slow_unique != quick_unique:
        raise ValueError(
            f"Uniqueness mismatch, slow says {slow_unique}, quick says {quick_unique} for uniqueness of board {board.puzzle_solution()}"
        )
    return slow_unique


# The "quick" generate functions use the code from count.py which pre-compute all boards
# of a certain size.


def quick_generate(
    n_pieces=None, min_pieces=4, max_pieces=7, no_mirror_balls=False, debug=False
):
    single_solution_boards = _match_boards(
        n_pieces=n_pieces,
        min_pieces=min_pieces,
        max_pieces=max_pieces,
        no_mirror_balls=no_mirror_balls,
    )

    val = choice(single_solution_boards)
    board = decode_board(val)

    # turn on all beams
    board.add_all_beams()

    if debug:
        print(f"Minimising board with pieces {board.pieces}...")
    return quick_minimise(board)


def quick_minimise(board):
    # restrict to boards and beams with desired pieces
    boards_with_pieces, beams_with_pieces = _boards_and_beams_for_pieces(
        board, fewer_pieces_allowed=True
    )

    # Turn each beam on and off
    num_beams = len(board.beams)

    min_boards = [board]
    min_num_beams = num_beams

    ball_on_two_ended_beam_allowed = "o" in board.pieces
    for ind in itertools.product((False, True), repeat=num_beams):
        new_board = board.copy()
        for x, y in board.beams[list(ind)][:, :2]:
            new_board.remove_beam(x + 1, y + 1)

        # and find matching boards
        matching_boards = _boards_for_beams(
            new_board,
            boards_with_pieces,
            beams_with_pieces,
            ball_on_two_ended_beam_allowed=ball_on_two_ended_beam_allowed,
        )
        unique = len(matching_boards) == 1
        if unique:
            if len(new_board.beams) < min_num_beams:
                min_boards = [new_board]
                min_num_beams = len(new_board.beams)
            elif len(new_board.beams) == min_num_beams:
                min_boards.append(new_board)

    # return one of the minimum boards
    return choice(min_boards)


def board_generator(
    n_pieces=None,
    min_pieces=4,
    max_pieces=7,
    no_mirror_balls=False,
    debug=False,
    quick=True,
):
    while True:
        if quick:
            yield quick_generate(
                n_pieces=n_pieces,
                min_pieces=min_pieces,
                max_pieces=max_pieces,
                no_mirror_balls=no_mirror_balls,
                debug=debug,
            )
        else:
            yield generate(
                n_pieces=n_pieces,
                min_pieces=min_pieces,
                max_pieces=max_pieces,
                no_mirror_balls=no_mirror_balls,
                debug=debug,
            )
