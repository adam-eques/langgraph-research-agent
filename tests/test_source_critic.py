from __future__ import annotations

from research_agent.agents.source_critic import assess_source, rank_sources_by_credibility


def test_trusted_domain_high_score():
    result = assess_source("https://arxiv.org/abs/2023.12345")
    assert result.is_trusted and result.score >= 0.8


def test_untrusted_domain_lower_score():
    result = assess_source("https://randomblog.net/article")
    assert not result.is_trusted


def test_no_https_flag():
    result = assess_source("http://example.com/page")
    assert "no_https" in result.flags


def test_rank_sources():
    urls = ["http://randomblog.net/", "https://arxiv.org/paper"]
    ranked = rank_sources_by_credibility(urls)
    assert ranked[0].domain == "arxiv.org"
