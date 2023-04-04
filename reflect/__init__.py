# flake8: noqa
from .board import (
    Block,
    Board,
    block_int_to_str_array,
    block_str_to_int_array,
    boards_are_unique,
)
from .difficulty import board_features
from .game import play_game
from .generate import generate
from .solve import (
    cproduct_idx,
    has_unique_solution,
    is_solution,
    piece_permutations,
    solve,
)
from .svg import print_svg
from .terminal import play_game_on_terminal
