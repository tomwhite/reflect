"""
Reflect puzzle.
"""
import datetime
import math
from time import time

import arcade

from reflect.difficulty import predict_solve_duration
from reflect.generate import generate

# Screen title and size
SCREEN_WIDTH = 240
SCREEN_HEIGHT = 360
SCREEN_TITLE = "Reflect"

BLOCK_SIZE = 40
CELL_SIZE = 38

SPRITE_NAMES = {
    "/": "oblique_mirror",
    "\\": "reverse_oblique_mirror",
    "o": "mirror_ball",
}

# https://sashamaps.net/docs/resources/20-colors/
COLOURS = [
    arcade.color_from_hex_string(colour)
    for colour in [
        "#e6194B",
        "#3cb44b",
        "#ffe119",
        "#4363d8",
        "#f58231",
        "#42d4f4",
        "#f032e6",
        "#fabed4",
        "#469990",
        "#dcbeff",
        "#9A6324",
        "#fffac8",
        "#800000",
        "#aaffc3",
        "#000075",
        "#a9a9a9",
    ]
]


class BlockSprite(arcade.Sprite):
    """Block sprite"""

    def __init__(self, piece, name, scale=1):
        self.piece = piece
        self.name = name

        # TODO: need to package these and use :resources: ?
        self.image_file_name = f"sprites/{self.name}_tr.png"

        super().__init__(self.image_file_name, scale, hit_box_algorithm="None")


class ReflectPuzzle(arcade.Window):
    def __init__(self, board, min_pieces, max_pieces):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        self.background = None

        self.original_board = board
        self.min_pieces = min_pieces
        self.max_pieces = max_pieces

        self.shape_list = None
        self.path_list = None

        # block sprites
        self.block_list = None
        self.block_cells = None

        # block currently being held (dragged)
        self.held_block = None
        self.held_block_original_position = None

        # cell sprites
        self.cell_list = None
        # dict mapping cell to index on board
        self.cell_indexes = None

        self.start_time = None
        self.solve_duration = math.inf
        self.first_click = False
        self.game_over = False

        arcade.set_background_color(arcade.color.WHITE)

    def setup(self):

        self.background = arcade.load_texture("sprites/reflect.png")

        if self.original_board is not None:
            self.board = self.original_board.copy()
        else:
            self.board = generate(
                min_pieces=self.min_pieces, max_pieces=self.max_pieces, debug=True
            )
            print(self.board.puzzle_string())
            print(f"Predicted solve duration: {predict_solve_duration(self.board)}")

        self.start_timestamp = datetime.datetime.now()

        self.shape_list = arcade.ShapeElementList()
        self.path_list = arcade.ShapeElementList()

        n = self.board.n

        beam_paths = self.board.beam_paths
        for bi, beam_path in enumerate(beam_paths):
            colour = COLOURS[bi]
            width = 5
            beam_path = beam_paths[bi]
            for bj in range(len(beam_path) - 1):
                start = beam_path[bj]
                end = beam_path[bj + 1]
                x0, y0 = block_index_to_coord(start[0], start[1])
                x1, y1 = block_index_to_coord(end[0], end[1])
                line = arcade.create_line(x0, y0, x1, y1, colour, width)
                self.path_list.append(line)

            start = beam_path[0]
            end = beam_path[-1]
            for i, j in (start, end):
                x, y = block_index_to_coord(i, j)
                if i == 0:
                    line = arcade.create_line(5, y, 40, y, colour, width)
                elif i == n + 1:
                    line = arcade.create_line(200, y, 235, y, colour, width)
                elif j == 0:
                    line = arcade.create_line(
                        x, flip_y(45), x, flip_y(80), colour, width
                    )
                elif j == n + 1:
                    line = arcade.create_line(
                        x, flip_y(240), x, flip_y(275), colour, width
                    )
                self.shape_list.append(line)

        for x in range(BLOCK_SIZE, BLOCK_SIZE * (n + 2), BLOCK_SIZE):
            line = arcade.create_line(
                x,
                flip_y(BLOCK_SIZE + 40),
                x,
                flip_y(BLOCK_SIZE * (n + 1) + 40),
                arcade.color.BLACK,
                1,
            )
            self.shape_list.append(line)
        for y in range(BLOCK_SIZE, BLOCK_SIZE * (n + 2), BLOCK_SIZE):
            line = arcade.create_line(
                BLOCK_SIZE,
                flip_y(y + 40),
                BLOCK_SIZE * (n + 1),
                flip_y(y + 40),
                arcade.color.BLACK,
                1,
            )
            self.shape_list.append(line)

        self.block_list = arcade.SpriteList()
        self.block_cells = {}

        self.cell_list: arcade.SpriteList = arcade.SpriteList()
        self.cell_indexes = {}

        for i, piece in enumerate(self.board.pieces):
            block = BlockSprite(piece, SPRITE_NAMES[piece])
            x, y = block_index_to_coord((i % 4) + 1, i // 4)
            y -= 240
            block.position = x, y
            self.block_list.append(block)
            cell = arcade.SpriteSolidColor(
                CELL_SIZE, CELL_SIZE, arcade.color.ALICE_BLUE
            )
            cell.position = block.position
            self.cell_list.append(cell)
            self.block_cells[cell] = block
        self.held_block = None
        self.held_block_original_position = None

        for i in range(self.board.n):
            for j in range(self.board.n):
                cell = arcade.SpriteSolidColor(
                    CELL_SIZE, CELL_SIZE, arcade.color.ALICE_BLUE
                )
                self.cell_indexes[cell] = (i, j)
                x, y = block_index_to_coord(i + 1, j + 1)
                cell.position = x, y
                self.cell_list.append(cell)

        self.start_time = None
        self.solve_duration = math.inf
        self.first_click = False
        self.game_over = False

    def on_draw(self):
        self.clear()
        arcade.draw_lrwh_rectangle_textured(
            0, flip_y(40), SCREEN_WIDTH, 40, self.background
        )
        self.shape_list.draw()
        if self.game_over:
            self.path_list.draw()
        else:
            self.cell_list.draw()
        self.block_list.draw()

    def pull_to_top(self, block: arcade.Sprite):
        self.block_list.remove(block)
        self.block_list.append(block)

    def move_block_to_cell(self, block, cell):
        prev_cell = None
        for c, b in dict(self.block_cells).items():
            if b == block:
                prev_cell = c
                break
        self.block_cells.pop(prev_cell)
        self.block_cells[cell] = block

        # update the board
        if prev_cell in self.cell_indexes:
            i, j = self.cell_indexes[prev_cell]
            self.board.set_value(i + 1, j + 1, ".")

        if cell in self.cell_indexes:
            i, j = self.cell_indexes[cell]
            self.board.set_value(i + 1, j + 1, self.held_block.piece)

    def on_mouse_press(self, x, y, button, key_modifiers):
        if not self.first_click:
            self.start_time = time()
            self.first_click = True
        if self.game_over:
            return

        blocks = arcade.get_sprites_at_point((x, y), self.block_list)

        if len(blocks) > 0:
            block = blocks[-1]  # they don't overlap, but get top one
            self.held_block = block
            self.held_block_original_position = self.held_block.position
            self.pull_to_top(self.held_block)

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
        if self.held_block is None:
            return

        cell, _ = arcade.get_closest_sprite(self.held_block, self.cell_list)
        reset_position = True
        if arcade.check_for_collision(self.held_block, cell):
            self.held_block.position = cell.center_x, cell.center_y
            if cell not in self.block_cells:  # not occupied
                self.block_cells[cell] = self.held_block
                self.move_block_to_cell(self.held_block, cell)
                reset_position = False
        if reset_position:
            self.held_block.position = self.held_block_original_position

        self.held_block = None

        if self.board.score() == 1:
            self.solve_duration = time() - self.start_time
            self.game_over = True

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        if self.held_block:
            self.held_block.center_x += dx
            self.held_block.center_y += dy

    def on_key_press(self, symbol: int, modifiers: int):
        """User presses key"""
        if symbol == arcade.key.R:
            self.setup()
        elif symbol == arcade.key.D:  # debug
            print(self.board)
        elif symbol in (
            arcade.key.KEY_1,
            arcade.key.KEY_2,
            arcade.key.KEY_3,
            arcade.key.KEY_4,
            arcade.key.KEY_5,
        ):
            difficulty = symbol - 48
            t = self.start_timestamp.isoformat(timespec="seconds")
            filename = f"puzzles/generated/puzzle-{t}.txt"
            game_duration = time() - self.start_time
            print(
                f"Saving to {filename} with difficulty {difficulty} with game duration {game_duration:.1f} and solve duration {self.solve_duration:.1f}"
            )
            with open(filename, "w") as f:
                f.write(f"# Generated at: {t}\n")
                f.write(f"# Difficulty: {difficulty}\n")
                f.write(f"# Game duration: {game_duration:.1f}\n")
                f.write(f"# Solve duration: {self.solve_duration:.1f}\n")
                f.write(self.board.puzzle_solution())
                f.write("\n")


def block_index_to_coord(i, j, x_offset=0, y_offset=40):
    x = i * BLOCK_SIZE + BLOCK_SIZE // 2 + x_offset
    y = flip_y(j * BLOCK_SIZE + BLOCK_SIZE // 2 + y_offset)
    return x, y


def flip_y(y):
    # convenience to flip y coordinate
    return SCREEN_HEIGHT - y


def play_game(board, min_pieces, max_pieces):
    window = ReflectPuzzle(board, min_pieces=min_pieces, max_pieces=max_pieces)
    window.setup()
    arcade.run()
