import base64
import io
import sys

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


def print_svg(board, show_solution=False, file=sys.stdout):

    return_svg = file is None
    if return_svg:
        from IPython.display import SVG

        file = io.StringIO()

    n = board.n

    print(
        """<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
""",
        file=file,
    )

    width = BLOCK_SIZE * (n + 2)
    height = BLOCK_SIZE * (n + 2)

    if not show_solution:
        height += BLOCK_SIZE * 2

    print(
        f'<svg width="{width}" height="{height}" version="1.1" xmlns="http://www.w3.org/2000/svg">',
        file=file,
    )

    # Sprites
    print("    <defs>", file=file)
    for sprite_name in SPRITE_NAMES.values():
        data_uri = image_to_data_uri(f"sprites/{sprite_name}_tr.png")
        print(
            f'        <image id="{sprite_name}" href="{data_uri}" height="{SPRITE_SIZE}" width="{SPRITE_SIZE}"/>',
            file=file,
        )
    print("    </defs>", file=file)

    # Beams
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
                f'    <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{colour}" stroke-width="{width}" />',
                file=file,
            )

    # Board lines
    for i in range(n):
        for j in range(n):
            print(
                f'    <rect x="{(i + 1) * BLOCK_SIZE}" y="{(j + 1) * BLOCK_SIZE}" width="{BLOCK_SIZE}" height="{BLOCK_SIZE}" stroke="black" fill="transparent" />',
                file=file,
            )

    # Beam paths
    if show_solution:
        for bi, beam_path in enumerate(beam_paths):
            colour = COLOURS[bi]
            width = 5
            beam_path = beam_paths[bi]
            for bj in range(len(beam_path) - 1):
                start = beam_path[bj]
                end = beam_path[bj + 1]
                x1, y1 = block_index_to_coord(start[0], start[1])
                x2, y2 = block_index_to_coord(end[0], end[1])
                print(
                    f'    <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{colour}" stroke-width="{width}" />',
                    file=file,
                )

    # Blocks
    if show_solution:
        for i in range(n):
            for j in range(n):
                x, y = block_index_to_coord(
                    j + 1, i + 1, x_offset=-SPRITE_SIZE // 2, y_offset=-SPRITE_SIZE // 2
                )
                piece = board.hidden_blocks[i, j]
                if piece == ".":
                    continue
                print(
                    f'    <use href="#{SPRITE_NAMES[piece]}" transform="translate({x}, {y})" />',
                    file=file,
                )
    else:
        for i, piece in enumerate(board.pieces):
            x, y = block_index_to_coord(
                (i % 4) + 1,
                i // 4,
                x_offset=-SPRITE_SIZE // 2,
                y_offset=BLOCK_SIZE * (n + 2) - SPRITE_SIZE // 2,
            )
            print(
                f'    <use href="#{SPRITE_NAMES[piece]}" transform="translate({x}, {y})" />',
                file=file,
            )

    print("</svg>", file=file)

    if return_svg:
        return SVG(file.getvalue())


def block_index_to_coord(i, j, x_offset=0, y_offset=0):
    x = int(i) * BLOCK_SIZE + BLOCK_SIZE // 2 + x_offset
    y = int(j) * BLOCK_SIZE + BLOCK_SIZE // 2 + y_offset
    return x, y


def image_to_data_uri(filename):
    ext = filename.split(".")[-1]
    prefix = f"data:image/{ext};base64,"
    with open(filename, "rb") as f:
        img = f.read()
    return prefix + base64.b64encode(img).decode("utf-8")
