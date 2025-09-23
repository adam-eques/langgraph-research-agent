from __future__ import annotations
import asyncio
from research_agent.agents.fact_extractor import (
    extract_facts, filter_high_confidence, deduplicate_facts, extract_facts_from_notes,
)


def test_extract_facts_basic():
    text = "Python was created in 1991. It is widely used for AI. Maybe it is the best."
    facts = extract_facts(text)
    assert len(facts) >= 2


def test_filter_high_confidence():
    facts = ["The sky is blue.", "It might rain tomorrow.", "Water boils at 100C."]
    filtered = filter_high_confidence(facts)
    assert all("might" not in f.lower() for f in filtered)


def test_deduplicate():
    facts = ["Python is great.", "Python is great.", "AI is powerful."]
    assert len(deduplicate_facts(facts)) == 2


def test_extract_facts_from_notes():
    notes = ["LangGraph enables stateful workflows. It might be slow.", "It is built on LangChain."]
    result = asyncio.run(extract_facts_from_notes(notes))
    assert isinstance(result, list)
