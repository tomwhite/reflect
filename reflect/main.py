import click

from reflect import Board
from reflect import generate as generate_board
from reflect import solve as solve_board


@click.group()
def cli():
    pass


@cli.command()
@click.argument("filename")
def solve(filename):
    with open(filename) as f:
        full_board = "".join([line for line in f.readlines()])
        board = Board.create(full_board=full_board)
        print(board.puzzle_string())
        print()

        print("Solutions:")
        print()
        solutions = solve_board(board)
        for solution in solutions:
            print(solution.puzzle_solution())
            print()


@cli.command()
@click.argument("filename")
def generate(filename):
    board = generate_board()
    print(board.puzzle_string())
    with open(filename, "w") as f:
        f.write(board.puzzle_solution())


if __name__ == "__main__":
    cli()
