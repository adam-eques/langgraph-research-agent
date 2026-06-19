from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ResearchGap:
    topic: str
    description: str
    priority: str = "medium"
    suggested_queries: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "topic": self.topic,
            "description": self.description,
            "priority": self.priority,
            "suggested_queries": self.suggested_queries,
        }


_UNCERTAINTY_MARKERS = [
    r"\bnot (yet )?(known|studied|understood|explored)\b",
    r"\blimited (research|evidence|data)\b",
    r"\bfurther (research|study|investigation) (is )?(needed|required)\b",
    r"\bremains? (unclear|unknown|unexplored)\b",
    r"\blittle is known\b",
]

_UNCERTAINTY_RE = [re.compile(p, re.I) for p in _UNCERTAINTY_MARKERS]


def detect_uncertainty(text: str) -> list[str]:
    matches: list[str] = []
    for pat in _UNCERTAINTY_RE:
        for m in pat.finditer(text):
            matches.append(m.group(0).strip())
    return matches


def identify_covered_topics(notes: list[str], min_length: int = 20) -> set[str]:
    topics: set[str] = set()
    for note in notes:
        words = note.split()
        for i in range(len(words) - 1):
            bigram = f"{words[i]} {words[i+1]}".lower()
            if len(bigram) >= min_length / 2:
                topics.add(bigram)
    return topics


def find_gaps(
    notes: list[str],
    required_topics: list[str] | None = None,
) -> list[ResearchGap]:
    gaps: list[ResearchGap] = []

    for note in notes:
        uncertainties = detect_uncertainty(note)
        if uncertainties:
            topic = note.split(".")[0][:60]
            gap = ResearchGap(
                topic=topic,
                description="; ".join(uncertainties[:3]),
                priority="high",
                suggested_queries=[f"review of {topic.lower()}", f"{topic.lower()} current research"],
            )
            gaps.append(gap)

    if required_topics:
        covered = identify_covered_topics(notes)
        for topic in required_topics:
            if not any(topic.lower() in c for c in covered):
                gaps.append(ResearchGap(
                    topic=topic,
                    description=f"Topic '{topic}' not covered in collected notes.",
                    priority="medium",
                    suggested_queries=[topic, f"{topic} overview"],
                ))

    return gaps


def prioritize_gaps(gaps: list[ResearchGap]) -> list[ResearchGap]:
    order = {"high": 0, "medium": 1, "low": 2}
    return sorted(gaps, key=lambda g: order.get(g.priority, 99))
