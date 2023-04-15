import random

import click

from reflect import Board
from reflect import generate as generate_board
from reflect import play_game, play_game_on_terminal, print_svg
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


@cli.command()
@click.argument("filename", required=False)
@click.option("--terminal", is_flag=True)
def play(filename, terminal):
    if filename is not None:
        with open(filename) as f:
            full_board = "".join([line for line in f.readlines()])
            board = Board.create(full_board=full_board)
    else:
        board = None
    if terminal:
        play_game_on_terminal(board)
    else:
        play_game(board)


@cli.command()
@click.argument("filename")
@click.option("--solution", is_flag=True)
def svg(filename, solution):
    with open(filename) as f:
        full_board = "".join([line for line in f.readlines()])
        board = Board.create(full_board=full_board)
        print_svg(board, show_solution=solution)


@cli.command()
@click.argument("input")
@click.argument("output")
def transform(input, output):
    with open(input) as fin, open(output, "w") as fout:
        lines = fin.readlines()
        full_board = "".join([line for line in lines])
        board = Board.create(full_board=full_board)
        board = random.choice(list(board.transforms()))
        fout.writelines([line for line in lines if line.startswith("#")])
        fout.write(board.puzzle_solution())


if __name__ == "__main__":
    cli()
