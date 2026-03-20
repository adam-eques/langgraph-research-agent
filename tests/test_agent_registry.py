from __future__ import annotations

import pytest
from research_agent.agent_registry import AgentRegistry


def test_register_and_get():
    reg = AgentRegistry()
    reg.register("researcher", lambda: "researcher_fn")
    assert reg.get("researcher") is not None


def test_get_missing_returns_none():
    reg = AgentRegistry()
    assert reg.get("nonexistent") is None


def test_is_registered():
    reg = AgentRegistry()
    reg.register("analyst", lambda: None)
    assert reg.is_registered("analyst") is True
    assert reg.is_registered("other") is False


def test_register_duplicate_raises():
    reg = AgentRegistry()
    reg.register("agent1", lambda: None)
    with pytest.raises(ValueError, match="already registered"):
        reg.register("agent1", lambda: None)


def test_list_agents_sorted():
    reg = AgentRegistry()
    reg.register("b_agent", lambda: None)
    reg.register("a_agent", lambda: None)
    assert reg.list_agents() == ["a_agent", "b_agent"]
