SCREEN_WIDTH = 240
SCREEN_HEIGHT = 360

BLOCK_SIZE = 40
CELL_SIZE = 38
SPRITE_SIZE = 32

SPRITE_NAMES = {
    "/": "oblique_mirror",
    "\\": "reverse_oblique_mirror",
    "o": "mirror_ball",
}

# https://sashamaps.net/docs/resources/20-colors/
COLOURS = [
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


def print_svg(board):
    print(
        """<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg width="240" height="360" version="1.1" xmlns="http://www.w3.org/2000/svg">
"""
    )

    # print the beams
    n = board.n

    beam_paths = board.beam_paths
    for bi, beam_path in enumerate(beam_paths):
        colour = COLOURS[bi]
        width = 5
        beam_path = beam_paths[bi]

        start = beam_path[0]
        end = beam_path[-1]
        for i, j in (start, end):
            x, y = block_index_to_coord(i, j)
            if i == 0:
                x1, y1 = 5, y
                x2, y2 = 40, y
            elif i == n + 1:
                x1, y1 = 200, y
                x2, y2 = 235, y
            elif j == 0:
                x1, y1 = x, 5
                x2, y2 = x, 40
            elif j == n + 1:
                x1, y1 = x, 200
                x2, y2 = x, 235
            print(
                f'    <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{colour}" stroke-width="{width}" />'
            )

    # print the pieces
    for i, piece in enumerate(board.pieces):
        x, y = block_index_to_coord((i % 4) + 1, i // 4)
        x -= BLOCK_SIZE // 2
        y += 240
        print(
            f'    <image href="sprites/{SPRITE_NAMES[piece]}.png" height="{SPRITE_SIZE}" width="{SPRITE_SIZE}" transform="translate({x}, {y})" />'
        )

    # print the grid
    for i in range(n):
        for j in range(n):
            print(
                f'    <rect x="{(i + 1) * BLOCK_SIZE}" y="{(j + 1) * BLOCK_SIZE}" width="{BLOCK_SIZE}" height="{BLOCK_SIZE}" stroke="black" fill="transparent" />'
            )

    print(
        """
</svg>"""
    )


def block_index_to_coord(i, j, x_offset=0, y_offset=0):
    x = i * BLOCK_SIZE + BLOCK_SIZE // 2 + x_offset
    y = j * BLOCK_SIZE + BLOCK_SIZE // 2 + y_offset
    return x, y
