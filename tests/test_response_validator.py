from __future__ import annotations

from research_agent.response_validator import validate_response


def test_valid_response():
    text = "Python is a high-level programming language used widely in data science and AI."
    result = validate_response(text)
    assert result.valid and result.score == 1.0


def test_empty_fails():
    result = validate_response("")
    assert not result.valid and "empty" in result.issues[0].lower()


def test_too_short_fails():
    result = validate_response("Yes.", min_chars=50)
    assert not result.valid


def test_refusal_detected():
    result = validate_response("As an AI, I cannot answer that question." * 3)
    assert not result.valid or len(result.issues) > 0


def test_score_range():
    result = validate_response("decent answer here " * 5)
    assert 0.0 <= result.score <= 1.0
