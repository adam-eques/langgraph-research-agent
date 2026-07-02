from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class Insight:
    text: str
    category: str
    confidence: float = 0.7
    keywords: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "category": self.category,
            "confidence": round(self.confidence, 4),
            "keywords": self.keywords,
        }


_CATEGORY_PATTERNS: dict[str, list[re.Pattern]] = {
    "finding": [
        re.compile(r"\b(study|research|analysis|data|experiment)\s+(shows?|reveals?|finds?|confirms?|suggests?)\b", re.I),
        re.compile(r"\baccording to\b", re.I),
    ],
    "trend": [
        re.compile(r"\b(increasing|decreasing|growing|declining|rising|falling)\b", re.I),
        re.compile(r"\bover (the past|recent)\s+\w+\b", re.I),
    ],
    "implication": [
        re.compile(r"\b(this means|therefore|thus|consequently|as a result)\b", re.I),
        re.compile(r"\bimplies?\b", re.I),
    ],
    "limitation": [
        re.compile(r"\b(however|but|although|despite|limitation|drawback)\b", re.I),
    ],
}


def classify_sentence(sentence: str) -> str:
    for category, patterns in _CATEGORY_PATTERNS.items():
        for pat in patterns:
            if pat.search(sentence):
                return category
    return "general"


def extract_keywords(text: str, top_n: int = 5) -> list[str]:
    stopwords = {"the", "a", "an", "is", "are", "was", "were", "it", "of", "and", "or", "in", "on", "at", "to"}
    words = re.findall(r"\b[a-z]{4,}\b", text.lower())
    freq: dict[str, int] = {}
    for w in words:
        if w not in stopwords:
            freq[w] = freq.get(w, 0) + 1
    return sorted(freq, key=lambda k: -freq[k])[:top_n]


def extract_insights(
    text: str,
    min_sentence_length: int = 30,
    min_confidence: float = 0.0,
) -> list[Insight]:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    insights: list[Insight] = []
    for sent in sentences:
        if len(sent) < min_sentence_length:
            continue
        category = classify_sentence(sent)
        confidence = 0.8 if category != "general" else 0.5
        if confidence >= min_confidence:
            insights.append(Insight(
                text=sent.strip(),
                category=category,
                confidence=confidence,
                keywords=extract_keywords(sent),
            ))
    return insights


def deduplicate_insights(insights: list[Insight], similarity_threshold: float = 0.7) -> list[Insight]:
    seen: list[str] = []
    result: list[Insight] = []
    for ins in insights:
        words = set(ins.text.lower().split())
        duplicate = False
        for prev in seen:
            prev_words = set(prev.lower().split())
            if words and prev_words:
                overlap = len(words & prev_words) / max(len(words), len(prev_words))
                if overlap >= similarity_threshold:
                    duplicate = True
                    break
        if not duplicate:
            seen.append(ins.text)
            result.append(ins)
    return result
