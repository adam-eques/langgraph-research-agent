from __future__ import annotations

from research_agent.source_ranker import (
    count_source_domains,
    extract_sources_from_notes,
    rank_sources_by_frequency,
)


def test_extract_sources():
    notes = ["See https://arxiv.org/abs/123 and https://openai.com/blog"]
    sources = extract_sources_from_notes(notes)
    assert "https://arxiv.org/abs/123" in sources
    assert "https://openai.com/blog" in sources


def test_extract_deduplicates():
    notes = ["See https://arxiv.org/abs/123", "Also https://arxiv.org/abs/123"]
    sources = extract_sources_from_notes(notes)
    assert len([s for s in sources if "arxiv.org" in s]) == 1


def test_count_source_domains():
    sources = ["https://arxiv.org/a", "https://arxiv.org/b", "https://openai.com"]
    counts = count_source_domains(sources)
    assert counts["arxiv.org"] == 2
    assert counts["openai.com"] == 1


def test_rank_sources_by_frequency():
    sources = ["https://arxiv.org/a", "https://arxiv.org/b", "https://openai.com"]
    ranked = rank_sources_by_frequency(sources)
    assert ranked[0][0] == "arxiv.org"
