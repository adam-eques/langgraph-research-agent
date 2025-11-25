from __future__ import annotations
from research_agent.agent_memory import AgentMemory


def test_add_and_get_turns():
    mem = AgentMemory()
    mem.add_turn("user", "Hello")
    mem.add_turn("assistant", "Hi there")
    assert mem.turn_count == 2


def test_remember_and_recall():
    mem = AgentMemory()
    mem.remember_fact("topic", "AI")
    assert mem.recall_fact("topic") == "AI"


def test_forget_fact():
    mem = AgentMemory()
    mem.remember_fact("key", "val")
    assert mem.forget_fact("key") is True and mem.recall_fact("key") is None


def test_to_messages():
    mem = AgentMemory()
    mem.add_turn("user", "What is RAG?")
    msgs = mem.to_messages()
    assert msgs[0]["role"] == "user" and "RAG" in msgs[0]["content"]


def test_max_turns_enforced():
    mem = AgentMemory(max_turns=3)
    for i in range(5):
        mem.add_turn("user", f"msg {i}")
    assert mem.turn_count == 3


def test_clear():
    mem = AgentMemory()
    mem.add_turn("user", "hi")
    mem.remember_fact("k", "v")
    mem.clear()
    assert mem.turn_count == 0 and mem.recall_fact("k") is None
