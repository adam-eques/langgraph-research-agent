from __future__ import annotations

import re
from typing import Any


def merge_notes(notes: list[str], dedup: bool = True) -> str:
    if dedup:
        seen, unique = set(), []
        for n in notes:
            key = re.sub(r"\s+", " ", n).strip().lower()[:80]
            if key not in seen:
                seen.add(key)
                unique.append(n)
        notes = unique
    return "\n\n".join(n.strip() for n in notes if n.strip())


def extract_key_sentences(text: str, n: int = 5) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text)
    long = [s for s in sentences if len(s.split()) >= 8]
    return long[:n]


def summarize_research_notes(notes: list[str], max_sentences: int = 10) -> str:
    merged = merge_notes(notes)
    key = extract_key_sentences(merged, n=max_sentences)
    return " ".join(key)
