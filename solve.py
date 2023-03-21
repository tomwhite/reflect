import sys

from reflect import Board, block_int_to_str_array, solve

if __name__ == "__main__":
    full_board_file = sys.argv[1]
    with open(full_board_file) as f:
        full_board = "".join(
            [line for line in f.readlines() if not line.startswith("#")]
        )
        full_board = full_board.strip()
        board = Board.create(full_board=full_board)
        print(board.puzzle_string())
        print()

        beams = board.beams
        pieces = board.pieces_ints

        print("Solutions:")
        print()
        solutions = solve(beams, pieces)
        for solution in solutions:
            solution_board = board.copy()
            solution_board.values[
                1 : board.n + 1, 1 : board.n + 1
            ] = block_int_to_str_array(solution)
            print(solution_board)
            print()
