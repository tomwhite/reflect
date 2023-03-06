import sys
from reflect import *

SPRITE_NAMES = {
    "/": "oblique_mirror",
    "\\": "reverse_oblique_mirror",
    "o": "mirror_ball",
}

def print_svg(board):
    print("""<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" 
"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg width="240" height="320" version="1.1" xmlns="http://www.w3.org/2000/svg">
""")
          
    # print the beams
    # from https://sashamaps.net/docs/resources/20-colors/ (99%)
    colours = ['#e6194B', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#42d4f4', '#f032e6', '#fabed4', '#469990', '#dcbeff', '#9A6324', '#fffac8', '#800000', '#aaffc3', '#000075', '#a9a9a9',]
    n = board.n
    beams = board.beams
    m = beams.shape[0]
    for i in range(m):
        colour = colours[i]
        width = 5
        x = beams[i, 0]
        y = beams[i, 1]
        if x == -1:
            print(f'    <line x1="5" y1="{20 + (y + 1) * 40}" x2="40" y2="{20 + (y + 1) * 40}" stroke="{colour}" stroke-width="{width}" />')
        elif x == n:
            print(f'    <line x1="200" y1="{20 + (y + 1) * 40}" x2="235" y2="{20 + (y + 1) * 40}" stroke="{colour}" stroke-width="{width}" />')
        elif y == -1:
            print(f'    <line x1="{20 + (x + 1) * 40}" y1="5" x2="{20 + (x + 1) * 40}" y2="40" stroke="{colour}" stroke-width="{width}" />')
        elif y == n:
            print(f'    <line x1="{20 + (x + 1) * 40}" y1="200" x2="{20 + (x + 1) * 40}" y2="235" stroke="{colour}" stroke-width="{width}" />')

        end_x = beams[i, 2]
        end_y = beams[i, 3]
        if end_x == x and end_y == y:
            # TODO: make line thicker?
            continue
        x, y = end_x, end_y

        # TODO: reduce duplication
        if x == -1:
            print(f'    <line x1="5" y1="{20 + (y + 1) * 40}" x2="40" y2="{20 + (y + 1) * 40}" stroke="{colour}" stroke-width="{width}" />')
        elif x == n:
            print(f'    <line x1="200" y1="{20 + (y + 1) * 40}" x2="235" y2="{20 + (y + 1) * 40}" stroke="{colour}" stroke-width="{width}" />')
        elif y == -1:
            print(f'    <line x1="{20 + (x + 1) * 40}" y1="5" x2="{20 + (x + 1) * 40}" y2="40" stroke="{colour}" stroke-width="{width}" />')
        elif y == n:
            print(f'    <line x1="{20 + (x + 1) * 40}" y1="200" x2="{20 + (x + 1) * 40}" y2="235" stroke="{colour}" stroke-width="{width}" />')

    # print the pieces
    for i, piece in enumerate(board.pieces):
        print(f'    <image href="sprites/{SPRITE_NAMES[piece]}.png" height="32" width="32" transform="translate({4 + i * 40}, 244)" />')
          
    # print the grid
    for i in range(4):
        for j in range(4):
            print(f'    <rect x="{(i + 1) * 40}" y="{(j + 1) * 40}" width="40" height="40" stroke="black" fill="transparent" />')
          
    print("""
</svg>""")

if __name__ == "__main__":
    full_board_file = sys.argv[1]
    with open(full_board_file) as f:
        full_board = "".join([line for line in f.readlines() if not line.startswith("#")])
        full_board = full_board.strip()
        board = Board.create(full_board=full_board)

        print_svg(board)