from __future__ import annotations

from research_agent.context_window_manager import ContextWindowManager


def test_add_and_retrieve():
    mgr = ContextWindowManager(max_tokens=1000)
    mgr.add("user", "Hello")
    mgr.add("assistant", "Hi there")
    assert mgr.message_count == 2


def test_trim_on_overflow():
    mgr = ContextWindowManager(max_tokens=10, chars_per_token=1)
    for i in range(20):
        mgr.add("user", "x")
    assert mgr.message_count < 20


def test_clear():
    mgr = ContextWindowManager()
    mgr.add("user", "test")
    mgr.clear()
    assert mgr.message_count == 0


def test_get_messages_returns_copy():
    mgr = ContextWindowManager()
    mgr.add("user", "q")
    msgs = mgr.get_messages()
    msgs.append({"role": "system", "content": "injected"})
    assert mgr.message_count == 1
