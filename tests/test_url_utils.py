from __future__ import annotations

from research_agent.url_utils import normalize_url, extract_domain, is_likely_paywalled


def test_normalize_url_strips_slash():
    assert normalize_url("https://example.com/") == "https://example.com"


def test_normalize_url_lowercases():
    assert normalize_url("HTTPS://Example.COM/path") == "https://example.com/path"


def test_extract_domain():
    assert extract_domain("https://arxiv.org/abs/1234.5678") == "arxiv.org"


def test_is_likely_paywalled_true():
    assert is_likely_paywalled("https://www.wsj.com/article") is True


def test_is_likely_paywalled_false():
    assert is_likely_paywalled("https://arxiv.org/abs/123") is False
