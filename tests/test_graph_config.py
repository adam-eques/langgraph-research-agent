from __future__ import annotations

from research_agent.graph_config import GraphConfig


def test_default_values():
    cfg = GraphConfig()
    assert cfg.model == "claude-3-5-sonnet-20241022"
    assert cfg.use_supervisor is False
    assert cfg.max_iterations == 10


def test_to_dict_has_keys():
    cfg = GraphConfig(use_rag=False)
    d = cfg.to_dict()
    assert "model" in d and "use_rag" in d
    assert d["use_rag"] is False


def test_from_dict_roundtrip():
    original = GraphConfig(temperature=0.5, max_tokens=2048)
    restored = GraphConfig.from_dict(original.to_dict())
    assert restored.temperature == 0.5
    assert restored.max_tokens == 2048


def test_custom_collection():
    cfg = GraphConfig(collection="my_docs")
    assert cfg.collection == "my_docs"
