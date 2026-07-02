from __future__ import annotations

from research_agent.agents.entity_linker import group_by_type, link_entities


def test_links_organization():
    text = "Google and Anthropic are working on AI systems."
    entities = link_entities(text)
    orgs = [e.text for e in entities if e.entity_type == "ORGANIZATION"]
    assert "Google" in orgs or "Anthropic" in orgs


def test_links_technology():
    text = "LangGraph and LangChain power modern agentic systems."
    entities = link_entities(text)
    techs = [e.text for e in entities if e.entity_type == "TECHNOLOGY"]
    assert len(techs) >= 1


def test_group_by_type():
    text = "OpenAI released GPT and Google released Gemini."
    entities = link_entities(text)
    grouped = group_by_type(entities)
    assert isinstance(grouped, dict)


def test_sorted_by_start():
    text = "Google and Anthropic are leaders."
    entities = link_entities(text)
    if len(entities) >= 2:
        assert entities[0].start <= entities[1].start
