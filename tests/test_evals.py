from devlens.evals import recall_at_k


def test_recall_at_k():
    assert recall_at_k(["a.py", "b.py"], {"a.py"}, 2) == 1.0
