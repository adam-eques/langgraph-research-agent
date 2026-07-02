from __future__ import annotations

from research_agent.multi_hop_planner import decompose_query, needs_multi_hop


def test_simple_query_single_hop():
    plan = decompose_query("What is LangGraph?")
    assert len(plan.hops) == 1


def test_multi_part_query_decomposed():
    plan = decompose_query("What is RAG then how does it work?")
    assert len(plan.hops) >= 2


def test_hop_dependencies():
    plan = decompose_query("Find papers on AI then summarize them")
    assert plan.hops[1].depends_on == [0]


def test_needs_multi_hop_true():
    assert needs_multi_hop("What is ML and then how do I apply it?") is True


def test_to_dict():
    plan = decompose_query("Q1 then Q2")
    d = plan.to_dict()
    assert "hops" in d and "original" in d
