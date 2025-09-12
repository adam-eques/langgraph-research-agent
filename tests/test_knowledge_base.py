from __future__ import annotations

from research_agent.knowledge_base import KnowledgeBase


def test_set_and_get(tmp_path):
    kb = KnowledgeBase(str(tmp_path / "kb.json"))
    kb.set("fact1", "The sky is blue")
    assert kb.get("fact1") == "The sky is blue"


def test_get_default(tmp_path):
    kb = KnowledgeBase(str(tmp_path / "kb.json"))
    assert kb.get("missing", "default") == "default"


def test_delete(tmp_path):
    kb = KnowledgeBase(str(tmp_path / "kb.json"))
    kb.set("k", "v")
    assert kb.delete("k") is True
    assert kb.get("k") is None


def test_keys(tmp_path):
    kb = KnowledgeBase(str(tmp_path / "kb.json"))
    kb.set("a", 1)
    kb.set("b", 2)
    assert set(kb.keys()) == {"a", "b"}


def test_clear(tmp_path):
    kb = KnowledgeBase(str(tmp_path / "kb.json"))
    kb.set("x", 1)
    kb.clear()
    assert kb.keys() == []
