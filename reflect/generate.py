import random

import numpy as np
from numpy.random import choice, shuffle

from reflect.board import Block, Board
from reflect.solve import has_unique_solution


def generate(n_pieces=None):
    if n_pieces is None:
        n_pieces = random.randrange(4, 8)
    for _ in range(20):
        print(f"Generating board with {n_pieces} blocks...")
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
        print(a)
        a = np.concatenate([a, np.full(16 - n_pieces, ".")])
        shuffle(a)
        a = a.reshape(4, 4)
        board = Board.create(hidden_blocks=a)
        for x, y in board.edge_locations():
            if board.values[y, x] == ".":
                board.add_beam(x, y)

        if has_unique_solution(board):
            print("Minimising board...")
            return minimise(board)

    # can't generate a board!
    raise ValueError("Failed to generate!")


def minimise(board):
    # try to remove beams at random while still having a unique solution

    best_board = board
    n_trials = 10

    for i in range(n_trials):
        print(f"Trial {i+1} of {n_trials}. Best board has {best_board.num_beams} beams")
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
            print(
                f"Finding if new board with {new_board.num_beams} beams has unique solution...",
                end=" ",
            )
            if not has_unique_solution(new_board):
                print("no")
                if prev_board.num_beams < best_board.num_beams:
                    best_board = prev_board
                break
            else:
                print("yes")

            prev_board = new_board

    return best_board
