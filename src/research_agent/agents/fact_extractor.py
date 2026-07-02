from __future__ import annotations

import re


def extract_facts(text: str) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    facts = []
    for s in sentences:
        s = s.strip()
        if len(s) > 20 and not s.lower().startswith(("i think", "maybe", "perhaps", "i believe")):
            facts.append(s)
    return facts


def filter_high_confidence(facts: list[str]) -> list[str]:
    hedge_words = {"might", "could", "possibly", "apparently", "allegedly", "seems"}
    return [f for f in facts if not any(w in f.lower().split() for w in hedge_words)]


def deduplicate_facts(facts: list[str]) -> list[str]:
    seen: set[str] = set()
    result = []
    for fact in facts:
        normalized = re.sub(r"\s+", " ", fact.lower().strip())
        if normalized not in seen:
            seen.add(normalized)
            result.append(fact)
    return result


async def extract_facts_from_notes(notes: list[str]) -> list[str]:
    all_facts: list[str] = []
    for note in notes:
        all_facts.extend(extract_facts(note))
    return deduplicate_facts(filter_high_confidence(all_facts))
