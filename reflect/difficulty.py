import collections
from statistics import mean

import numpy as np
import pandas as pd

from reflect.board import Block


def board_features(board):
    """
    Compute various board features, which can be used to characterize
    the difficulty of the puzzle.
    """
    n = board.n
    num_blocks = len(board.pieces)
    num_mirror_balls = len(
        [piece for piece in board.pieces if piece == Block.MIRROR_BALL.char]
    )

    beam_paths = board.beam_paths
    num_beams = len(beam_paths)

    # walk along each path and count number of blocks
    blocks_per_beam = []
    reflections_per_beam = []
    min_reflections_per_beam = []
    # also count number of beams for each block
    block_counts = collections.Counter()  # also count number of beams for each block
    # and the total number of reflections (not including mirror balls)
    num_reflections = 0
    for path in beam_paths:
        count = 0
        num_reflections_on_path = 0
        for loc in path:
            i, j = loc
            if board.on_inner_board(i, j):
                if board.hidden_blocks[j - 1, i - 1] != ".":
                    count += 1
                    block_counts.update([loc])
                    # treat ball as end of path for purposes of difficulty rating
                    if board.hidden_blocks[j - 1, i - 1] == "o":
                        break
                    else:
                        num_reflections += 1
                        num_reflections_on_path += 1
        blocks_per_beam.append(count)
        reflections_per_beam.append(num_reflections_on_path)

        # calculate minimum reflections on a path (not including mirror balls)
        start_loc = path[0]
        end_loc = path[-1]
        # change end loc to mirror ball if there is one
        for loc in path:
            i, j = loc
            if board.on_inner_board(i, j):
                if board.hidden_blocks[j - 1, i - 1] == "o":
                    end_loc = loc
        min_blocks = minimum_blocks_on_path(board, start_loc, end_loc)
        min_reflections_per_beam.append(min_blocks)

    mean_blocks_per_beam = mean(blocks_per_beam)
    max_blocks_per_beam = max(blocks_per_beam)
    num_multi_block_beams = sum([i > 1 for i in blocks_per_beam])

    beams_per_block = list(block_counts.values())
    mean_beams_per_block = mean(beams_per_block)
    max_beams_per_block = max(beams_per_block)
    num_double_reflect_blocks = sum([n_beams == 2 for n_beams in beams_per_block])

    # treat ball as end of path for purposes of difficulty rating
    def distance(path):
        contains_ball = False
        for loc in path:
            i, j = loc
            if board.on_inner_board(i, j):
                if board.hidden_blocks[j - 1, i - 1] == "o":
                    contains_ball = True
        if contains_ball:
            return (len(path) - 1) // 2
        else:
            return len(path) - 1

    def manhattan_distance(path):
        start_loc = path[0]
        end_loc = path[-1]
        # change end loc to mirror ball if there is one
        for loc in path:
            i, j = loc
            if board.on_inner_board(i, j):
                if board.hidden_blocks[j - 1, i - 1] == "o":
                    end_loc = loc

        dist = abs(start_loc[0] - end_loc[0]) + abs(start_loc[1] - end_loc[1])

        # correct for when start and end are on same side of board
        if start_loc[0] == end_loc[0] and start_loc[0] in (0, n + 1):
            dist += 2
        elif start_loc[1] == end_loc[1] and start_loc[1] in (0, n + 1):
            dist += 2

        return dist

    beam_distances = [distance(path) for path in beam_paths]
    mean_beam_distance = mean(beam_distances)
    max_beam_distance = max(beam_distances)
    total_beam_distance = sum(beam_distances)

    manhattan_distances = [manhattan_distance(path) for path in beam_paths]
    excess_beam_distance = total_beam_distance - sum(manhattan_distances)

    num_zero_reflection_blocks = num_blocks - len(beams_per_block)

    # excess reflections - the number of extra mirror blocks needed above naive minimum
    excess_reflections = num_reflections - sum(min_reflections_per_beam)
    num_excess_reflection_beams = sum(
        np.array(reflections_per_beam) > np.array(min_reflections_per_beam)
    )

    return dict(
        num_blocks=num_blocks,
        num_mirror_balls=num_mirror_balls,
        num_beams=num_beams,
        num_reflections=num_reflections,
        mean_blocks_per_beam=mean_blocks_per_beam,
        max_blocks_per_beam=max_blocks_per_beam,
        num_multi_block_beams=num_multi_block_beams,
        mean_beams_per_block=mean_beams_per_block,
        max_beams_per_block=max_beams_per_block,
        num_double_reflect_blocks=num_double_reflect_blocks,
        mean_beam_distance=mean_beam_distance,
        max_beam_distance=max_beam_distance,
        total_beam_distance=total_beam_distance,
        excess_beam_distance=excess_beam_distance,
        num_zero_reflection_blocks=num_zero_reflection_blocks,
        excess_reflections=excess_reflections,
        num_excess_reflection_beams=num_excess_reflection_beams,
    )


def minimum_blocks_on_path(board, start_loc, end_loc):
    """Calculate the minimum number of blocks needed to reflect
    a beam from the start to end location.
    """

    assert start_loc != end_loc

    sx, sy = start_loc
    ex, ey = end_loc

    assert board.on_edge(sx, sy)

    # case when end location is a mirror ball on the board
    if board.on_inner_board(ex, ey):
        if sx == ex or sy == ey:  # same row or column
            return 0
        else:
            return 1

    assert board.on_edge(ex, ey)

    sn = edge_number(board, sx, sy)
    en = edge_number(board, ex, ey)
    if sn == en:  # same edge
        return 2
    elif abs(sn - en) % 2 == 1:  # adjacent edges
        return 1
    elif abs(sn - en) == 2:  # opposite edges
        if sx == ex or sy == ey:  # same row or column
            return 0
        else:
            return 2

    raise ValueError(
        f"Error calculating minimum_blocks_on_path for {start_loc} -> {end_loc}"
    )


def edge_number(board, x, y):
    assert board.on_edge(x, y)
    # anticlockwise, starting with left edge
    if x == 0:
        return 0
    elif y == board.n + 1:
        return 1
    elif x == board.n + 1:
        return 2
    elif y == 0:
        return 3


def predict_solve_duration(board):
    # train a random forest model on all data
    # and use it to predict solve duration of new board

    all_df = pd.read_csv("data/all.csv")

    train_df = all_df[
        all_df["median_solve_duration_s"] < 1000
    ]  # remove outliers for model

    feature_names = [
        "num_blocks",
        "num_mirror_balls",
        "num_beams",
        "num_reflections",
        "max_blocks_per_beam",
        "num_double_reflect_blocks",
        "excess_reflections",
    ]

    response_variable = "median_solve_duration_s"

    X_train = train_df[feature_names]
    y_train = train_df[[response_variable]].values.ravel()

    from sklearn.ensemble import RandomForestRegressor

    model = RandomForestRegressor()
    model.fit(X_train, y_train)

    features = board_features(board)

    X = pd.DataFrame.from_records([features])[feature_names]

    y_pred = model.predict(X)

    print(predict_solve_duration_linear_regression(board))

    return y_pred[0]


def predict_solve_duration_linear_regression(board):
    features = board_features(board)
    max_blocks_per_beam = features["max_blocks_per_beam"]

    from joblib import load

    X = [[max_blocks_per_beam]]
    model = load("model.joblib")
    y_pred = model.predict(X)
    return y_pred[0, 0]
