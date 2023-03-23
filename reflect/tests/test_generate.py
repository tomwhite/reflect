from reflect import generate, has_unique_solution


def test_generate():
    board = generate(n_pieces=4)
    assert has_unique_solution(board)
