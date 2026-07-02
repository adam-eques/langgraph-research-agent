from __future__ import annotations

from research_agent.eval.scorer import composite_score, score_answer_length, score_citation_coverage


def test_length_score_in_range():
    answer = " ".join(["word"] * 100)
    assert score_answer_length(answer) == 1.0


def test_length_score_too_short():
    answer = "short answer"
    score = score_answer_length(answer, min_words=50)
    assert score < 1.0 and score > 0.0


def test_citation_coverage_empty():
    assert score_citation_coverage("any text", []) == 1.0


def test_composite_score_range():
    answer = " ".join(["word"] * 100)
    score = composite_score(answer, [], 0.8, 0.9)
    assert 0.0 <= score <= 1.0
