import collections
from statistics import mean


def board_features(board):
    """
    Compute various board features, which can be used to characterize
    the difficulty of the puzzle.
    """
    num_blocks = len(board.pieces)
    beam_paths = board.beam_paths
    num_beams = len(beam_paths)

    # walk along each path and count number of blocks
    blocks_per_beam = []
    # also count number of beams for each block
    block_counts = collections.Counter()  # also count number of beams for each block
    for path in beam_paths:
        count = 0
        for loc in path:
            i, j = loc
            if board.on_inner_board(i, j):
                if board.hidden_blocks[j - 1, i - 1] != ".":
                    count += 1
                    block_counts.update([loc])
        blocks_per_beam.append(count)
    mean_blocks_per_beam = mean(blocks_per_beam)
    max_blocks_per_beam = max(blocks_per_beam)

    beams_per_block = list(block_counts.values())
    mean_beams_per_block = mean(beams_per_block)
    max_beams_per_block = max(beams_per_block)

    beam_distances = [len(path) - 1 for path in beam_paths]
    mean_beam_distance = mean(beam_distances)
    max_beam_distance = max(beam_distances)

    num_zero_reflection_blocks = num_blocks - len(beams_per_block)

    return dict(
        num_blocks=num_blocks,
        num_beams=num_beams,
        mean_blocks_per_beam=mean_blocks_per_beam,
        max_blocks_per_beam=max_blocks_per_beam,
        mean_beams_per_block=mean_beams_per_block,
        max_beams_per_block=max_beams_per_block,
        mean_beam_distance=mean_beam_distance,
        max_beam_distance=max_beam_distance,
        num_zero_reflection_blocks=num_zero_reflection_blocks,
    )


def predict_solve_duration(board):
    features = board_features(board)
    max_blocks_per_beam = features["max_blocks_per_beam"]

    from joblib import load

    X = [[max_blocks_per_beam]]
    model = load("model.joblib")
    y_pred = model.predict(X)
    return y_pred[0, 0]
