from __future__ import annotations

from research_agent.agents.insight_extractor import (
    Insight,
    classify_sentence,
    deduplicate_insights,
    extract_insights,
    extract_keywords,
)


def test_classify_finding():
    sent = "The study shows that exercise improves cognitive function significantly."
    assert classify_sentence(sent) == "finding"


def test_classify_trend():
    sent = "The number of users is increasing rapidly over recent years."
    assert classify_sentence(sent) == "trend"


def test_classify_implication():
    sent = "This means that companies must adapt their strategies accordingly."
    assert classify_sentence(sent) == "implication"


def test_extract_keywords():
    text = "machine learning models require large datasets for training purposes"
    kw = extract_keywords(text)
    assert "machine" in kw or "learning" in kw or "models" in kw


def test_extract_insights_basic():
    text = (
        "The research reveals that sleep deprivation affects memory consolidation. "
        "This is a well-known short fact. "
        "Therefore, adequate sleep is essential for learning and retention of information."
    )
    insights = extract_insights(text)
    assert len(insights) >= 1


def test_deduplicate_insights():
    ins = [
        Insight("AI is transforming the healthcare industry.", "finding"),
        Insight("AI is transforming the healthcare industry significantly.", "finding"),
        Insight("Quantum computing will revolutionize cryptography completely.", "implication"),
    ]
    unique = deduplicate_insights(ins, similarity_threshold=0.6)
    assert len(unique) < len(ins)
