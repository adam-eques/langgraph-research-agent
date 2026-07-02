from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class SourceCredibility:
    url: str
    domain: str
    score: float
    flags: list[str]
    is_trusted: bool


_TRUSTED_DOMAINS = {
    "arxiv.org",
    "nature.com",
    "science.org",
    "pubmed.ncbi.nlm.nih.gov",
    "ieee.org",
    "acm.org",
    "dl.acm.org",
    "scholar.google.com",
    "github.com",
    "docs.python.org",
    "pytorch.org",
    "tensorflow.org",
    "anthropic.com",
    "openai.com",
    "huggingface.co",
}

_SUSPICIOUS_PATTERNS = [
    r"click.*?here",
    r"buy now",
    r"sponsored",
    r"affiliate",
    r"advertisement",
    r"promo",
    r"referral",
]


def assess_source(url: str, content: str = "") -> SourceCredibility:
    domain = url.split("/")[2] if "://" in url else url
    if domain.startswith("www."):
        domain = domain[4:]
    flags: list[str] = []
    score = 0.5

    if domain in _TRUSTED_DOMAINS:
        score += 0.4
    elif domain.endswith(".edu") or domain.endswith(".gov"):
        score += 0.3
    elif domain.endswith(".org"):
        score += 0.1

    if content:
        for pat in _SUSPICIOUS_PATTERNS:
            if re.search(pat, content, re.I):
                flags.append("suspicious_content")
                score -= 0.1
                break

    if not url.startswith("https://"):
        flags.append("no_https")
        score -= 0.05

    score = max(0.0, min(1.0, score))
    return SourceCredibility(
        url=url,
        domain=domain,
        score=round(score, 3),
        flags=flags,
        is_trusted=domain in _TRUSTED_DOMAINS,
    )


def rank_sources_by_credibility(sources: list[str]) -> list[SourceCredibility]:
    assessed = [assess_source(url) for url in sources]
    return sorted(assessed, key=lambda s: s.score, reverse=True)
