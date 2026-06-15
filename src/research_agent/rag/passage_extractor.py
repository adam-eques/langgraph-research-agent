from __future__ import annotations

import re


def extract_relevant_passages(
    text: str,
    query_terms: list[str],
    window_sentences: int = 3,
    max_passages: int = 5,
) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    if not sentences:
        return []

    query_lower = {t.lower() for t in query_terms}
    scored: list[tuple[float, int]] = []

    for i, sent in enumerate(sentences):
        words = re.findall(r"\b\w+\b", sent.lower())
        hits = sum(1 for w in words if w in query_lower)
        if hits > 0:
            scored.append((hits / max(len(words), 1), i))

    scored.sort(reverse=True)
    passages: list[str] = []
    seen_centers: set[int] = set()

    for _, center in scored[:max_passages]:
        if center in seen_centers:
            continue
        seen_centers.add(center)
        start = max(0, center - window_sentences // 2)
        end = min(len(sentences), center + window_sentences - window_sentences // 2)
        passage = " ".join(sentences[start:end])
        if passage.strip():
            passages.append(passage.strip())

    return passages


def highlight_terms(text: str, terms: list[str]) -> str:
    for term in terms:
        text = re.sub(re.escape(term), f"**{term}**", text, flags=re.IGNORECASE)
    return text
