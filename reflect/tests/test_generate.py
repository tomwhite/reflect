from reflect import generate, has_unique_solution, quick_generate


def test_generate():
    board = generate(n_pieces=4)
    assert has_unique_solution(board)


def test_quick_generate():
    board = quick_generate(n_pieces=5)
    assert has_unique_solution(board)  # check slow way
