from __future__ import annotations

from research_agent.output_ranker import rank_answers


def test_rank_answers_returns_sorted():
    candidates = [
        {"answer": "AI is artificial intelligence", "faithfulness": 0.9},
        {"answer": "sports news", "faithfulness": 0.3},
    ]
    ranked = rank_answers(candidates, "What is AI?")
    assert ranked[0]["answer"] == "AI is artificial intelligence"


def test_rank_adds_score():
    candidates = [{"answer": "test answer", "faithfulness": 0.7}]
    ranked = rank_answers(candidates, "test query")
    assert "_score" in ranked[0]


def test_rank_empty():
    assert rank_answers([], "q") == []
