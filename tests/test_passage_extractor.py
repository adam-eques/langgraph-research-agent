from __future__ import annotations
from research_agent.rag.passage_extractor import extract_relevant_passages, highlight_terms


def test_extracts_relevant_passage():
    text = "AI is transforming the world. Neural networks are at the core. Deep learning drives progress."
    passages = extract_relevant_passages(text, ["neural", "networks"])
    assert any("Neural" in p or "neural" in p for p in passages)


def test_max_passages_limit():
    text = " ".join(f"Sentence about AI number {i}." for i in range(20))
    passages = extract_relevant_passages(text, ["AI"], max_passages=3)
    assert len(passages) <= 3


def test_no_hits_returns_empty():
    text = "The weather is nice today. Birds are singing."
    passages = extract_relevant_passages(text, ["python", "machine"])
    assert passages == []


def test_highlight_terms():
    result = highlight_terms("LangGraph is great for AI agents.", ["LangGraph", "AI"])
    assert "**LangGraph**" in result and "**AI**" in result
