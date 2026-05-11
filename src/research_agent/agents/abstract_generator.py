from __future__ import annotations

import re
from typing import Any


def generate_abstract(
    title: str,
    sections: list[str],
    max_chars: int = 800,
) -> str:
    key_sentences: list[str] = []
    for section in sections:
        sentences = re.split(r"(?<=[.!?])\s+", section.strip())
        significant = [s for s in sentences if len(s) > 40]
        if significant:
            key_sentences.append(significant[0])

    combined = " ".join(key_sentences)
    if len(combined) > max_chars:
        combined = combined[:max_chars].rsplit(" ", 1)[0] + "..."

    if title:
        return f"This paper explores {title.lower()}. {combined}"
    return combined


def extract_contributions(text: str) -> list[str]:
    patterns = [
        r"(?:we|this work|this paper)\s+(?:propose[sd]?|present[sd]?|introduce[sd]?|develop[sd]?)\s+(.+?)(?:\.|,)",
        r"(?:our|the)\s+(?:main|key|primary|novel)\s+contribution[s]?\s+(?:is|are)\s+(.+?)(?:\.|,)",
    ]
    contributions = []
    for pat in patterns:
        for m in re.finditer(pat, text, re.IGNORECASE):
            contributions.append(m.group(1).strip())
    return list(dict.fromkeys(contributions))[:5]


def format_abstract(abstract: str, contributions: list[str]) -> dict[str, Any]:
    return {
        "abstract": abstract,
        "key_contributions": contributions,
        "word_count": len(abstract.split()),
    }
