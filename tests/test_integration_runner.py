from __future__ import annotations


def test_import():
    from research_agent.integration_runner import run_full_pipeline

    assert callable(run_full_pipeline)
