from __future__ import annotations
from research_agent.query_history import QueryHistory


def test_add_and_recent(tmp_path):
    qh = QueryHistory(str(tmp_path / "qh.jsonl"))
    qh.add("What is AI?", "s1")
    qh.add("What is ML?", "s1")
    assert len(qh.recent(n=5)) == 2


def test_search(tmp_path):
    qh = QueryHistory(str(tmp_path / "qh.jsonl"))
    qh.add("machine learning tutorial")
    qh.add("sports news")
    assert len(qh.search("machine")) == 1


def test_for_session(tmp_path):
    qh = QueryHistory(str(tmp_path / "qh.jsonl"))
    qh.add("q1", session_id="A")
    qh.add("q2", session_id="B")
    assert len(qh.for_session("A")) == 1


def test_meta_stored(tmp_path):
    qh = QueryHistory(str(tmp_path / "qh.jsonl"))
    qh.add("query with meta", meta={"source": "api"})
    assert qh.recent(1)[0]["meta"]["source"] == "api"
