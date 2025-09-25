from __future__ import annotations
from research_agent.agents.topic_modeler import (
    extract_keywords, group_by_topic, infer_topic_label, tokenize,
)


def test_tokenize():
    tokens = tokenize("Hello world, this is Python!")
    assert "python" in tokens and "hello" in tokens


def test_extract_keywords():
    text = "machine learning machine learning deep learning neural networks"
    kw = extract_keywords(text, top_n=3)
    assert "machine" in kw or "learning" in kw


def test_group_by_topic():
    docs = ["Python is used for machine learning", "JavaScript is for web development"]
    groups = group_by_topic(docs, ["python", "javascript"])
    assert 0 in groups["python"] and 1 in groups["javascript"]


def test_infer_topic_label():
    docs = ["neural networks deep learning AI", "deep learning optimization"]
    label = infer_topic_label(docs)
    assert isinstance(label, str) and len(label) > 0
