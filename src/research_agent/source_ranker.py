from __future__ import annotations

import re


def extract_sources_from_notes(notes: list[str]) -> list[str]:
    """Extract URLs and source references from research notes."""
    sources = []
    url_pattern = re.compile(r"https?://[^\s\)\"\']+")
    for note in notes:
        sources.extend(url_pattern.findall(note))
    return list(dict.fromkeys(sources))  # deduplicate preserving order


def count_source_domains(sources: list[str]) -> dict[str, int]:
    """Count occurrences of each domain in source list."""
    from research_agent.url_utils import extract_domain

    counts: dict[str, int] = {}
    for url in sources:
        domain = extract_domain(url)
        counts[domain] = counts.get(domain, 0) + 1
    return counts


def rank_sources_by_frequency(sources: list[str]) -> list[tuple[str, int]]:
    counts = count_source_domains(sources)
    return sorted(counts.items(), key=lambda x: x[1], reverse=True)
