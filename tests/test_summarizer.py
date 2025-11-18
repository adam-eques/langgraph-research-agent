from __future__ import annotations

from research_agent.summarizer import extractive_summary


def test_extractive_summary_returns_n_sentences():
    text = "First sentence. Second sentence. Third sentence. Fourth sentence."
    result = extractive_summary(text, n_sentences=2)
    assert "First sentence" in result
    assert "Third sentence" not in result


def test_extractive_summary_short_text():
    text = "Only one sentence."
    result = extractive_summary(text, n_sentences=3)
    assert result == text
