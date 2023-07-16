import csv
import math
import random
import re
from pathlib import Path

import click

from reflect import Board, board_features
from reflect import generate as generate_board
from reflect import play_game, play_game_on_terminal, predict_solve_duration, print_svg
from reflect import solve as solve_board
from reflect.count import compute_and_save_all_puzzles
from reflect.stats import (
    compute_per_device_stats,
    compute_stats,
    load_features,
    load_firebase_events,
    merge_stats_and_features,
)


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
        solutions = solve_board(
            board, fewer_pieces_allowed=True, ball_on_two_ended_beam_allowed=True
        )
        for solution in solutions:
            print(solution.puzzle_solution())
            print()


@cli.command()
@click.argument("filename")
@click.option("--min-pieces", default=4)
@click.option("--max-pieces", default=7)
def generate(filename, min_pieces, max_pieces):
    board = generate_board(min_pieces=min_pieces, max_pieces=max_pieces)
    print(board.puzzle_string())
    with open(filename, "w") as f:
        f.write(board.puzzle_solution())


@cli.command()
@click.argument("filename", required=False)
@click.option("--terminal", is_flag=True)
@click.option("--min-pieces", default=4)
@click.option("--max-pieces", default=7)
@click.option("--no-mirror-balls", is_flag=True)
@click.option("--quick", is_flag=True)
def play(filename, terminal, min_pieces, max_pieces, no_mirror_balls, quick):
    if filename is not None:
        with open(filename) as f:
            full_board = "".join([line for line in f.readlines()])
            board = Board.create(full_board=full_board)
    else:
        board = None
    if terminal:
        play_game_on_terminal(board)
    else:
        play_game(
            board,
            min_pieces=min_pieces,
            max_pieces=max_pieces,
            no_mirror_balls=no_mirror_balls,
            quick=quick,
        )


@cli.command()
@click.argument("filename")
@click.option("--solution", is_flag=True)
def svg(filename, solution):
    with open(filename) as f:
        full_board = "".join([line for line in f.readlines()])
        board = Board.create(full_board=full_board)
        print_svg(board, show_solution=solution)


@cli.command()
@click.argument("directory", type=click.Path(exists=True, file_okay=False))
@click.argument("output-directory", type=click.Path(exists=True, file_okay=False))
@click.option("--solution", is_flag=True)
def svgs(directory, output_directory, solution):
    files = Path(directory).glob("*.txt")
    out_dir = Path(output_directory)
    for full_board_file in sorted(files):
        with open(full_board_file) as f:
            full_board = "".join([line for line in f.readlines()])
            board = Board.create(full_board=full_board)
            out_file = out_dir / f"{full_board_file.stem}.svg"
            with open(out_file, "w") as out:
                print_svg(board, show_solution=solution, file=out)


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


@cli.command()
@click.argument("directory", type=click.Path(exists=True, file_okay=False))
@click.argument("output")
def features(directory, output):
    all_features = []
    files = Path(directory).glob("*.txt")
    for full_board_file in sorted(files):
        with open(full_board_file) as f:
            lines = f.readlines()
            setter_solve_duration = math.nan
            for line in lines:
                if match := re.search("Difficulty: (\\d+)", line):
                    difficulty = match.group(1)
                if match := re.search("Solve duration: (.+)", line):
                    setter_solve_duration = match.group(1)
            full_board = "".join([line for line in lines])
            board = Board.create(full_board=full_board)
            features = board_features(board)
            features["filename"] = full_board_file.name
            features["difficulty"] = difficulty
            features["setter_solve_duration_s"] = setter_solve_duration
            all_features.append(features)

    with open(output, "w", newline="") as csvfile:
        fieldnames = list(all_features[0].keys())
        # make sure "filename is first
        fieldnames.remove("filename")
        fieldnames.insert(0, "filename")
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for feature in all_features:
            writer.writerow(feature)


@cli.command()
@click.argument("output")
def stats(output):
    events_df = load_firebase_events()
    device_df = compute_per_device_stats(events_df)
    stats_df = compute_stats(events_df, device_df)
    features_df = load_features()
    all_df = merge_stats_and_features(stats_df, features_df)
    all_df.to_csv(output, index=False)


@cli.command()
@click.argument("input")
def predict(input):
    with open(input) as fin:
        lines = fin.readlines()
        full_board = "".join([line for line in lines])
        board = Board.create(full_board=full_board)

        predicted_solve_duration = predict_solve_duration(board)
        print(predicted_solve_duration)


@cli.command()
@click.argument("output")
def save_all_puzzles(output):
    compute_and_save_all_puzzles(max_pieces=7, filename=output)


if __name__ == "__main__":
    cli()
