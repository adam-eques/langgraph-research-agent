from __future__ import annotations

from research_agent.citation_index import CitationIndex


def test_add_and_retrieve():
    idx = CitationIndex()
    idx.add({"source": "arxiv.org", "excerpt": "paper A"})
    assert len(idx.by_source("arxiv.org")) == 1


def test_top_sources():
    idx = CitationIndex()
    idx.add({"source": "arxiv.org"})
    idx.add({"source": "arxiv.org"})
    idx.add({"source": "openai.com"})
    top = idx.top_sources(n=2)
    assert top[0][0] == "arxiv.org" and top[0][1] == 2


def test_all_citations_count():
    idx = CitationIndex()
    idx.add({"source": "a.com"})
    idx.add({"source": "b.com"})
    assert len(idx.all_citations()) == 2


def test_sources_list():
    idx = CitationIndex()
    idx.add({"source": "x.com"})
    assert "x.com" in idx.sources()
