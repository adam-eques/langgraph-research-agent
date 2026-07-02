from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass


@dataclass
class KeyTerm:
    term: str
    frequency: int
    weight: float
    is_phrase: bool = False

    def to_dict(self) -> dict:
        return {
            "term": self.term,
            "frequency": self.frequency,
            "weight": round(self.weight, 4),
            "is_phrase": self.is_phrase,
        }


_STOPWORDS = frozenset(
    "the a an and or but in on at to for of with by from is are was were be been being "
    "have has had do does did will would could should may might shall can "
    "that this these those it its there their they we you he she i me my".split()
)

_PHRASE_RE = re.compile(r"\b([A-Z][a-z]+(?:\s[A-Z][a-z]+)+)\b")


def extract_single_terms(text: str, min_freq: int = 1) -> list[KeyTerm]:
    words = re.findall(r"\b[a-z]{4,}\b", text.lower())
    freq = Counter(w for w in words if w not in _STOPWORDS)
    max_freq = max(freq.values(), default=1)
    return [
        KeyTerm(
            term=w,
            frequency=c,
            weight=c / max_freq,
        )
        for w, c in freq.most_common()
        if c >= min_freq
    ]


def extract_named_phrases(text: str) -> list[KeyTerm]:
    phrases = _PHRASE_RE.findall(text)
    freq = Counter(phrases)
    max_freq = max(freq.values(), default=1)
    return [
        KeyTerm(term=p, frequency=c, weight=c / max_freq, is_phrase=True)
        for p, c in freq.most_common()
    ]


def extract_key_terms(
    text: str,
    top_n: int = 10,
    include_phrases: bool = True,
    min_freq: int = 1,
) -> list[KeyTerm]:
    terms = extract_single_terms(text, min_freq=min_freq)
    if include_phrases:
        terms = extract_named_phrases(text) + terms
    seen: set[str] = set()
    unique: list[KeyTerm] = []
    for t in terms:
        if t.term.lower() not in seen:
            seen.add(t.term.lower())
            unique.append(t)
    return sorted(unique, key=lambda t: -t.weight)[:top_n]
