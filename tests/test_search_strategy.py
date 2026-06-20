from __future__ import annotations

from research_agent.search_strategy import SearchConfig, build_search_config


def test_default_config():
    cfg = SearchConfig()
    assert cfg.strategy == "hybrid"
    assert cfg.top_k == 5
    assert cfg.rerank is True


def test_factual_config():
    cfg = build_search_config("factual", ["web", "rag"])
    assert cfg.strategy == "semantic"
    assert cfg.top_k == 3


def test_comparative_config():
    cfg = build_search_config("comparative", ["web", "rag"])
    assert cfg.expand_queries is True
    assert cfg.top_k == 8


def test_no_web_source():
    cfg = build_search_config("factual", ["rag"])
    assert cfg.use_web is False
