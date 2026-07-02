from __future__ import annotations

from research_agent.session_store import SessionStore


def test_save_and_load(tmp_path):
    store = SessionStore(str(tmp_path / "sessions"))
    store.save("sess1", {"query": "what is AI?", "turn": 1})
    data = store.load("sess1")
    assert data["query"] == "what is AI?"


def test_load_missing_returns_none(tmp_path):
    store = SessionStore(str(tmp_path / "sessions"))
    assert store.load("nonexistent") is None


def test_delete_session(tmp_path):
    store = SessionStore(str(tmp_path / "sessions"))
    store.save("sess2", {"x": 1})
    assert store.delete("sess2") is True
    assert store.load("sess2") is None


def test_list_sessions(tmp_path):
    store = SessionStore(str(tmp_path / "sessions"))
    store.save("a", {})
    store.save("b", {})
    sessions = store.list_sessions()
    assert len(sessions) == 2
