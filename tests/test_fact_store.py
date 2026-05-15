from __future__ import annotations

from research_agent.fact_store import FactStore


def test_add_and_search(tmp_path):
    store = FactStore(str(tmp_path / "facts.jsonl"))
    store.add("AI is transforming industries", "arxiv.org", confidence=0.9)
    results = store.search("AI")
    assert len(results) == 1
    assert "AI" in results[0]["fact"]


def test_high_confidence_filter(tmp_path):
    store = FactStore(str(tmp_path / "facts.jsonl"))
    store.add("Fact A", "source1", confidence=0.95)
    store.add("Fact B", "source2", confidence=0.5)
    hc = store.high_confidence(threshold=0.8)
    assert len(hc) == 1
    assert hc[0]["fact"] == "Fact A"


def test_all_facts(tmp_path):
    store = FactStore(str(tmp_path / "facts.jsonl"))
    store.add("f1", "s1")
    store.add("f2", "s2")
    assert len(store.all_facts()) == 2
