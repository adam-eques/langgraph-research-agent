from __future__ import annotations

from research_agent.prompts import (
    analyst_system_prompt,
    build_system_prompt,
    researcher_system_prompt,
)


def test_build_system_prompt_basic():
    prompt = build_system_prompt("a researcher", "Research the query.")
    assert "You are a researcher." in prompt
    assert "Research the query." in prompt


def test_build_system_prompt_with_constraints():
    prompt = build_system_prompt("an agent", "task", constraints=["Do not lie", "Cite sources"])
    assert "- Do not lie" in prompt
    assert "- Cite sources" in prompt


def test_researcher_prompt_has_constraints():
    prompt = researcher_system_prompt()
    assert "Cite sources" in prompt
    assert "research assistant" in prompt


def test_analyst_prompt_has_output_format():
    prompt = analyst_system_prompt()
    assert "JSON" in prompt
    assert "confidence" in prompt


def test_researcher_prompt_includes_context():
    prompt = researcher_system_prompt("extra context here")
    assert "extra context here" in prompt
