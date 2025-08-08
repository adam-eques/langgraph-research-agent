from __future__ import annotations

from research_agent.pipeline import ResearchPipeline


def test_pipeline_runs_steps():
    p = ResearchPipeline()
    p.add("upper", str.upper)
    p.add("strip", str.strip)
    result = p.run("  hello  ")
    assert result == "HELLO"


def test_pipeline_disabled_step():
    p = ResearchPipeline()
    p.add("upper", str.upper)
    p.disable("upper")
    result = p.run("hello")
    assert result == "hello"


def test_step_names():
    p = ResearchPipeline()
    p.add("a", lambda x: x).add("b", lambda x: x)
    assert p.step_names == ["a", "b"]


def test_empty_pipeline():
    p = ResearchPipeline()
    assert p.run("data") == "data"
