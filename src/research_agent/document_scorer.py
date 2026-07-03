from __future__ import annotations

import re


def score_document_quality(text: str) -> float:
    """Estimate document quality as a score in [0, 1]."""
    if not text.strip():
        return 0.0
    words = text.split()
    word_count = len(words)
    avg_word_len = sum(len(w) for w in words) / max(word_count, 1)
    # Penalize very short documents
    length_score = min(1.0, word_count / 100)
    # Penalize very short or very long average word length (boilerplate heuristic)
    word_len_score = 1.0 - abs(avg_word_len - 5) / 10
    word_len_score = max(0.0, min(1.0, word_len_score))
    # Reward sentences (structured writing)
    sentence_count = len(re.findall(r"[.!?]+", text))
    sentence_score = min(1.0, sentence_count / 5)
    return round((length_score + word_len_score + sentence_score) / 3, 3)


def filter_low_quality(documents: list[str], threshold: float = 0.4) -> list[str]:
    return [d for d in documents if score_document_quality(d) >= threshold]
