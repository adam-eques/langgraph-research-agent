from __future__ import annotations

from research_agent.pipeline_config import PipelineConfig


def test_defaults():
    cfg = PipelineConfig()
    assert cfg.enable_rag is True and cfg.retrieval_top_k == 5


def test_to_dict_roundtrip():
    cfg = PipelineConfig(max_search_results=20, llm_model="gpt-4")
    d = cfg.to_dict()
    cfg2 = PipelineConfig.from_dict(d)
    assert cfg2.max_search_results == 20 and cfg2.llm_model == "gpt-4"


def test_with_overrides():
    cfg = PipelineConfig()
    cfg2 = cfg.with_overrides(temperature=0.0, enable_web_search=False)
    assert cfg2.temperature == 0.0 and cfg2.enable_web_search is False
    assert cfg.temperature == 0.3


def test_tags_and_metadata():
    cfg = PipelineConfig(tags=["v2"], metadata={"owner": "adam"})
    assert "v2" in cfg.tags and cfg.metadata["owner"] == "adam"
