from __future__ import annotations

from research_agent.eval.result import EvalResult, threshold_check


def test_mean_score_empty():
    r = EvalResult("q", "e", "g")
    assert r.mean_score == 0.0


def test_mean_score_with_values():
    r = EvalResult("q", "e", "g", scores={"relevance": 0.8, "faithfulness": 0.9})
    assert abs(r.mean_score - 0.85) < 0.001


def test_threshold_check_passes():
    r = EvalResult("q", "e", "g", scores={"relevance": 0.8, "faithfulness": 0.7})
    result = threshold_check(r, threshold=0.6)
    assert result.passed is True


def test_threshold_check_fails():
    r = EvalResult("q", "e", "g", scores={"relevance": 0.5, "faithfulness": 0.9})
    result = threshold_check(r, threshold=0.6)
    assert result.passed is False


def test_to_dict_keys():
    r = EvalResult("q", "e", "g", scores={"relevance": 0.9})
    d = r.to_dict()
    assert "query" in d and "mean_score" in d and "passed" in d
