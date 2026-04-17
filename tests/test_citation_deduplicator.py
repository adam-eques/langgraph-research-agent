from __future__ import annotations

from research_agent.citation_deduplicator import deduplicate_citations, merge_citation_lists, normalize_source


def test_normalize_source():
    assert normalize_source("https://arxiv.org/abs/123/") == "arxiv.org/abs/123"


def test_deduplicate_same_source():
    citations = [
        {"source": "https://arxiv.org/abs/1"},
        {"source": "https://arxiv.org/abs/1"},
        {"source": "https://openai.com"},
    ]
    result = deduplicate_citations(citations)
    assert len(result) == 2


def test_merge_citation_lists():
    a = [{"source": "https://a.com"}]
    b = [{"source": "https://b.com"}, {"source": "https://a.com"}]
    result = merge_citation_lists(a, b)
    assert len(result) == 2
