from __future__ import annotations

import pytest

from research_agent.prompt_versioner import PromptVersioner


@pytest.fixture
def versioner(tmp_path):
    path = str(tmp_path / "prompts.json")
    return PromptVersioner(store_path=path)


def test_register_returns_digest(versioner):
    digest = versioner.register("researcher", "You are a researcher.")
    assert len(digest) == 12


def test_register_same_prompt_no_duplicate(versioner):
    versioner.register("researcher", "prompt text")
    versioner.register("researcher", "prompt text")
    assert len(versioner.list_versions("researcher")) == 1


def test_get_latest_returns_most_recent(versioner):
    versioner.register("researcher", "v1 prompt")
    versioner.register("researcher", "v2 prompt")
    assert versioner.get_latest("researcher") == "v2 prompt"


def test_list_versions_empty_for_unknown(versioner):
    assert versioner.list_versions("unknown") == []


def test_register_different_prompts(versioner):
    versioner.register("analyst", "v1")
    versioner.register("analyst", "v2")
    assert len(versioner.list_versions("analyst")) == 2
