from __future__ import annotations

import re
from collections import Counter

_STOPWORDS = {
    "the",
    "a",
    "an",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "have",
    "has",
    "had",
    "do",
    "does",
    "did",
    "will",
    "would",
    "could",
    "should",
    "may",
    "might",
    "shall",
    "can",
    "need",
    "dare",
    "ought",
    "to",
    "of",
    "in",
    "on",
    "at",
    "by",
    "for",
    "with",
    "about",
    "against",
    "between",
    "into",
    "through",
    "during",
    "before",
    "after",
    "above",
    "and",
    "but",
    "or",
    "nor",
    "not",
    "so",
    "yet",
    "both",
    "either",
    "it",
    "its",
    "this",
    "that",
    "these",
    "those",
    "i",
    "we",
    "you",
    "he",
    "she",
    "they",
    "what",
    "which",
    "who",
    "whom",
    "how",
    "when",
    "where",
}


def tokenize(text: str) -> list[str]:
    return [w.lower() for w in re.findall(r"\b[a-z]{3,}\b", text.lower())]


def extract_keywords(text: str, top_n: int = 10) -> list[str]:
    tokens = [t for t in tokenize(text) if t not in _STOPWORDS]
    return [word for word, _ in Counter(tokens).most_common(top_n)]


def group_by_topic(
    documents: list[str],
    topics: list[str],
    top_n: int = 3,
) -> dict[str, list[int]]:
    topic_docs: dict[str, list[int]] = {t: [] for t in topics}
    for i, doc in enumerate(documents):
        kw = set(extract_keywords(doc, top_n=20))
        scores = {t: len(kw & set(tokenize(t))) for t in topics}
        best = max(scores, key=lambda k: scores[k])
        topic_docs[best].append(i)
    return topic_docs


def infer_topic_label(documents: list[str], top_n: int = 5) -> str:
    all_text = " ".join(documents)
    keywords = extract_keywords(all_text, top_n=top_n)
    return ", ".join(keywords) if keywords else "general"
