import random

import numpy as np
from numpy.random import choice, shuffle

from reflect.board import Block, Board
from reflect.solve import has_unique_solution


def generate(n_pieces=None):
    if n_pieces is None:
        n_pieces = random.randrange(4, 7)
    for _ in range(20):
        a = choice(
            np.array(
                [
                    Block.OBLIQUE_MIRROR.char,
                    Block.REVERSE_OBLIQUE_MIRROR.char,
                    Block.MIRROR_BALL.char,
                ]
            ),
            p=np.array([2 / 5, 2 / 5, 1 / 5]),
            size=n_pieces,
        )
        a = np.concatenate([a, np.full(16 - n_pieces, ".")])
        shuffle(a)
        a = a.reshape(4, 4)
        board = Board.create(hidden_blocks=a)
        for x, y in board.edge_locations():
            if board.values[y, x] == ".":
                board.add_beam(x, y)

        if has_unique_solution(board):
            return minimise(board)

    # can't generate a board!
    raise ValueError("Failed to generate!")


def minimise(board):
    # try to remove beams at random while still having a unique solution

    best_board = board

    for _ in range(10):
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
            if not has_unique_solution(new_board):
                if prev_board.num_beams < best_board.num_beams:
                    best_board = prev_board
                break

            prev_board = new_board

    return best_board
