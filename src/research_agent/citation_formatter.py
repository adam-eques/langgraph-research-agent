from __future__ import annotations

import re


def format_apa(source: str, title: str = "", year: str = "") -> str:
    domain = re.search(r"://([^/]+)", source)
    domain.group(1) if domain else source
    parts = []
    if title:
        parts.append(title + ".")
    if year:
        parts.append(f"({year}).")
    parts.append(f"Retrieved from {source}")
    return " ".join(parts) if parts else f"Retrieved from {source}"


def format_inline_citation(index: int, source: str) -> str:
    domain = re.search(r"://([^/]+)", source)
    host = domain.group(1) if domain else source
    return f"[{index}]({host})"


def build_references_section(citations: list[dict]) -> str:
    if not citations:
        return ""
    lines = ["## References", ""]
    for i, c in enumerate(citations, 1):
        source = c.get("source", "unknown")
        title = c.get("title", "")
        year = c.get("year", "")
        lines.append(f"{i}. {format_apa(source, title, year)}")
    return "\n".join(lines)
