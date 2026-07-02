from __future__ import annotations
from research_agent.result_aggregator import aggregate_results, merge_answers, AggregatedResult


def test_aggregate_basic():
    results = [
        {"answer": "AI is machine intelligence", "source": "src1", "confidence": 0.9},
        {"answer": "AI uses algorithms", "source": "src2", "confidence": 0.8},
    ]
    agg = aggregate_results("What is AI?", results)
    assert agg.best_answer == "AI is machine intelligence"
    assert agg.confidence == 0.85


def test_aggregate_deduplicates_sources():
    results = [{"source": "s1"}, {"source": "s1"}, {"source": "s2"}]
    agg = aggregate_results("Q", results)
    assert len(agg.sources) == 2


def test_to_dict():
    agg = AggregatedResult("Q", ["ans"], ["src"], 0.9, {})
    d = agg.to_dict()
    assert "best_answer" in d and "confidence" in d


def test_merge_answers_deduplicates():
    merged = merge_answers(["AI answer", "AI answer", "ML answer"])
    assert merged.count("AI answer") == 1
