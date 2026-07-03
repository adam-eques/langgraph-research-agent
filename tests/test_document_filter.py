from __future__ import annotations

from research_agent.rag.document_filter import (
    apply_filters,
    filter_by_metadata_key,
    filter_by_min_length,
    filter_by_score,
    filter_by_source_domain,
)


def test_filter_by_min_length():
    docs = [{"content": "short"}, {"content": "x" * 200}]
    assert len(filter_by_min_length(docs, 100)) == 1


def test_filter_by_score():
    docs = [{"content": "a", "score": 0.3}, {"content": "b", "score": 0.8}]
    assert len(filter_by_score(docs, min_score=0.5)) == 1


def test_filter_by_source_domain():
    docs = [
        {"content": "a", "source": "https://spam.com/page"},
        {"content": "b", "source": "https://legit.org/page"},
    ]
    result = filter_by_source_domain(docs, {"spam.com"})
    assert len(result) == 1 and "legit" in result[0]["source"]


def test_filter_by_metadata_key():
    docs = [{"metadata": {"lang": "en"}}, {"metadata": {"lang": "fr"}}]
    result = filter_by_metadata_key(docs, "lang", "en")
    assert len(result) == 1


def test_apply_filters_combined():
    docs = [
        {"content": "x" * 200, "score": 0.9, "source": "https://ok.com/p"},
        {"content": "short", "score": 0.9},
    ]
    result = apply_filters(docs, min_length=100, min_score=0.5)
    assert len(result) == 1
