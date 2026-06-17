from __future__ import annotations
import time
from research_agent.session_manager import SessionManager


def test_create_and_get(tmp_path):
    sm = SessionManager(str(tmp_path), ttl=3600)
    session = sm.create()
    retrieved = sm.get(session.session_id)
    assert retrieved is session and sm.active_count == 1


def test_add_turn():
    from research_agent.session_manager import Session
    s = Session("test-id")
    s.add_turn("user", "Hello")
    assert len(s.history) == 1 and s.history[0]["role"] == "user"


def test_cleanup_expired(tmp_path):
    sm = SessionManager(str(tmp_path), ttl=0.001)
    sm.create()
    time.sleep(0.01)
    count = sm.cleanup_expired()
    assert count == 1 and sm.active_count == 0


def test_expire(tmp_path):
    sm = SessionManager(str(tmp_path))
    s = sm.create()
    assert sm.expire(s.session_id) is True and sm.active_count == 0
