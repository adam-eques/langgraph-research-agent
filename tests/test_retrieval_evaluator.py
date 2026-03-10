from __future__ import annotations

from research_agent.retrieval_evaluator import precision_at_k, recall_at_k, mean_reciprocal_rank, evaluate_retrieval


def test_precision_at_k():
    retrieved = ["a", "b", "c", "d"]
    relevant = ["a", "c"]
    assert precision_at_k(retrieved, relevant, k=4) == 0.5


def test_recall_at_k():
    retrieved = ["a", "b"]
    relevant = ["a", "b", "c"]
    assert recall_at_k(retrieved, relevant, k=2) > 0.5


def test_mrr_first_hit():
    retrieved = ["a", "b", "c"]
    assert mean_reciprocal_rank(retrieved, ["a"]) == 1.0


def test_mrr_no_hit():
    retrieved = ["x", "y"]
    assert mean_reciprocal_rank(retrieved, ["z"]) == 0.0


def test_evaluate_retrieval_returns_dict():
    result = evaluate_retrieval(["a", "b"], ["a"], k=2)
    assert "precision_at_k" in result and "mrr" in result
