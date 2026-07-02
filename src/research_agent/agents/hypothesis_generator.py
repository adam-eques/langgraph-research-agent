from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class Hypothesis:
    statement: str
    basis: list[str] = field(default_factory=list)
    confidence: float = 0.5
    testable: bool = True

    def to_dict(self) -> dict:
        return {
            "statement": self.statement,
            "basis": self.basis,
            "confidence": round(self.confidence, 4),
            "testable": self.testable,
        }


_HYPOTHESIS_TEMPLATES = [
    "It is hypothesized that {subject} leads to {effect}.",
    "We propose that {subject} is correlated with {effect}.",
    "Evidence suggests that {subject} may influence {effect}.",
]

_CAUSAL_PATTERNS = [
    re.compile(r"(\w[\w\s]+?)\s+causes?\s+([\w\s]+)", re.I),
    re.compile(r"(\w[\w\s]+?)\s+(?:increases?|decreases?)\s+([\w\s]+)", re.I),
    re.compile(r"(\w[\w\s]+?)\s+leads?\s+to\s+([\w\s]+)", re.I),
]


def extract_causal_pairs(text: str) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for pat in _CAUSAL_PATTERNS:
        for m in pat.finditer(text):
            subj = m.group(1).strip()
            eff = m.group(2).strip()
            if len(subj) > 2 and len(eff) > 2:
                pairs.append((subj, eff))
    return pairs


def generate_hypotheses(
    research_notes: list[str],
    max_hypotheses: int = 5,
) -> list[Hypothesis]:
    hypotheses: list[Hypothesis] = []
    for note in research_notes:
        for subj, eff in extract_causal_pairs(note):
            stmt = f"It is hypothesized that {subj} leads to {eff}."
            h = Hypothesis(
                statement=stmt,
                basis=[note[:120]],
                confidence=0.55,
                testable=True,
            )
            hypotheses.append(h)
            if len(hypotheses) >= max_hypotheses:
                return hypotheses
    return hypotheses


def filter_testable(hypotheses: list[Hypothesis]) -> list[Hypothesis]:
    return [h for h in hypotheses if h.testable]


def rank_by_confidence(hypotheses: list[Hypothesis]) -> list[Hypothesis]:
    return sorted(hypotheses, key=lambda h: h.confidence, reverse=True)
