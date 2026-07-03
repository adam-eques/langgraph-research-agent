from __future__ import annotations

from research_agent.agents.summary_ranker import (
    RankedSummary,
    rank_summaries,
    score_summary,
    select_best,
)


def test_score_higher_with_keywords():
    keywords = ["machine", "learning"]
    good = "Machine learning algorithms improve over time with more training data."
    bad = "The weather today is sunny and warm outside."
    assert score_summary(good, keywords) > score_summary(bad, keywords)


def test_rank_summaries_ordering():
    keywords = ["python", "async"]
    summaries = [
        "Async Python makes concurrent code easier to write and reason about.",
        "The capital of France is Paris.",
    ]
    ranked = rank_summaries(summaries, keywords)
    assert ranked[0].rank == 1 and ranked[0].keyword_hits >= ranked[1].keyword_hits


def test_rank_assigns_rank_field():
    summaries = ["A", "B", "C"]
    ranked = rank_summaries(summaries, [])
    assert sorted(r.rank for r in ranked) == [1, 2, 3]


def test_select_best_returns_string():
    summaries = [
        "LangGraph is a stateful multi-agent framework for building research tools.",
        "It is raining.",
    ]
    best = select_best(summaries, ["langgraph", "multi-agent", "stateful"])
    assert best is not None and isinstance(best, str)


def test_select_best_empty():
    assert select_best([], []) is None


def test_ranked_summary_to_dict():
    rs = RankedSummary("some text", 0.75, 9, 2, rank=1)
    d = rs.to_dict()
    assert d["rank"] == 1 and d["score"] == 0.75
