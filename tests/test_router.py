from __future__ import annotations

import pytest

from research_agent.router import QueryRouter


@pytest.fixture
def router():
    return QueryRouter()


def test_routes_rag_on_document_keyword(router):
    assert router.route("summarize the uploaded document") == "rag"


def test_routes_web_on_latest_keyword(router):
    assert router.route("what is the latest news on AI") == "web"


def test_routes_supervisor_on_compare_keyword(router):
    assert router.route("compare and analyze GPT-4 vs Claude") == "supervisor"


def test_routes_default_for_generic_query(router):
    assert router.route("what is machine learning") == "linear"


def test_stats_increment(router):
    router.route("document about climate")
    router.route("recent AI news")
    assert router.stats["rag"] == 1
    assert router.stats["web"] == 1
