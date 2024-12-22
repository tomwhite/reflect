import math
from datetime import datetime

import numpy as np
import pandas as pd

SOLVE_DURATION_DIFFICULTY_BINS = [-np.inf, 100, 250, 500, np.inf]
SOLVE_DURATION_DIFFICULTY_CATEGORIES = ["easy", "medium", "hard", "superhard"]


def load_firebase_events(path="results.json"):
    """Load events from the JSON file exported from firebase."""
    df = pd.read_json(path, lines=True)
    df = df[["puzzle", "name", "device", "timestamp"]]
    today = datetime.today().strftime("%Y-%m-%d")
    df = df[df["puzzle"] != today]
    # coerce will set invalid date to NaT, which we then filter out with notnull
    df["date"] = pd.to_datetime(df["puzzle"], errors="coerce", format="%Y-%m-%d")
    df = df[df["date"].notnull()]
    return df


def compute_solve_duration(group):
    """The time between the last 'first move' event before the first 'solved' event, and that 'solved' event."""

    events = group["name"].tolist()
    if "firstMove" not in events:
        return math.nan  # wasn't started
    if "solved" not in events:
        return np.inf  # wasn't solved

    # filter out preload events, and sort by timestamp
    group_playing = group[group["name"] != "preload"].sort_values(by=["timestamp"])

    last_first_move_time_before_solved = math.nan
    first_solve_time = math.nan
    for _, row in group_playing.iterrows():
        if row["name"] == "firstMove":
            last_first_move_time_before_solved = row["timestamp"]
        elif row["name"] == "solved":
            first_solve_time = row["timestamp"]
            break  # ignore any more events (e.g. if solved again)
    # following guards against cases where events were out of order for some (unknown) reason
    if isinstance(last_first_move_time_before_solved, float) and math.isnan(
        last_first_move_time_before_solved
    ):
        return math.nan
    return (first_solve_time - last_first_move_time_before_solved).total_seconds()


def compute_per_device_stats(events_df):
    """Group events by puzzle and device, and compute solve durations.

    A duration of `inf` means that the puzzle wasn't solved, and `nan` means it wasn't started.
    """
    grouped = events_df.groupby(["puzzle", "date", "device"])

    device_df = grouped.apply(compute_solve_duration)
    device_df = device_df.reset_index(name="solve_duration_s")

    return device_df


def compute_stats(events_df, device_df):
    """Compute global stats."""

    # number of players per day
    players_df = (
        events_df.groupby("puzzle")
        .agg("nunique")
        .rename(columns={"device": "n_players"})
    )
    players_df = players_df[["n_players"]]

    # number of puzzles started per day
    started_df = events_df[events_df["name"] == "firstMove"]
    started_df = (
        started_df.groupby("puzzle")
        .agg("nunique")
        .rename(columns={"device": "n_started"})
    )
    started_df = started_df[["n_started"]]

    # number of puzzles solved per day
    solved_df = events_df[events_df["name"] == "solved"]
    solved_df = (
        solved_df.groupby("puzzle")
        .agg("nunique")
        .rename(columns={"device": "n_solved"})
    )
    solved_df = solved_df[["n_solved"]]

    # merge
    stats_df = pd.merge(players_df, started_df, on="puzzle")
    stats_df = pd.merge(stats_df, solved_df, on="puzzle")

    # success and failure rates
    stats_df["success_rate"] = 100 * stats_df["n_solved"] / stats_df["n_started"]
    stats_df["failure_rate"] = 100 - stats_df["success_rate"]
    stats_df

    # calculate median solve duration for each puzzle
    # note that puzzles that weren't solved (but were started) a value of inf is taken account of,
    # whereas nan (not started) are filtered out
    solve_durations_df = device_df[device_df["solve_duration_s"].notnull()]
    solve_duration_stats_df = solve_durations_df.groupby("puzzle")[
        "solve_duration_s"
    ].median()
    solve_duration_stats_df = solve_duration_stats_df.reset_index(
        name="median_solve_duration_s"
    )

    stats_df = pd.merge(stats_df, solve_duration_stats_df, on="puzzle")

    # difficulty based on solve duration
    stats_df["difficulty_duration"] = pd.cut(
        stats_df["median_solve_duration_s"],
        SOLVE_DURATION_DIFFICULTY_BINS,
        labels=SOLVE_DURATION_DIFFICULTY_CATEGORIES,
    )

    # add back date column
    stats_df["date"] = pd.to_datetime(stats_df["puzzle"], format="%Y-%m-%d")

    return stats_df


def load_features(path="features.csv"):
    df = pd.read_csv(path)
    df[["puzzle"]] = df.filename.str.extract(r"puzzle-(.+).txt", expand=True)
    return df


def merge_stats_and_features(stats_df, features_df):
    return pd.merge(stats_df, features_df, on="puzzle")


if __name__ == "__main__":
    events_df = load_firebase_events()
    print(events_df)

    device_df = compute_per_device_stats(events_df)
    print(device_df)

    stats_df = compute_stats(events_df, device_df)
    print(stats_df)

    features_df = load_features()
    print(features_df)

    all_df = merge_stats_and_features(stats_df, features_df)
    print(all_df)
