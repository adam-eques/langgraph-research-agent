from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class NarrativeSegment:
    content: str
    segment_type: str
    order: int

    def to_dict(self) -> dict:
        return {
            "content": self.content,
            "type": self.segment_type,
            "order": self.order,
        }


_TRANSITION_WORDS = {
    "contrast": ["however", "on the other hand", "nevertheless", "although", "yet"],
    "cause": ["therefore", "thus", "as a result", "consequently", "hence"],
    "addition": ["furthermore", "in addition", "moreover", "additionally", "also"],
    "sequence": ["first", "then", "next", "finally", "subsequently"],
}


def add_transition(prev_type: str, next_type: str) -> str:
    if prev_type == "finding" and next_type == "limitation":
        return "However, "
    if prev_type == "finding" and next_type == "implication":
        return "Therefore, "
    if prev_type == "limitation" and next_type == "finding":
        return "Nevertheless, "
    return ""


def build_narrative(
    fragments: list[dict],
    topic: str = "",
    max_segments: int = 20,
) -> list[NarrativeSegment]:
    if not fragments:
        return []

    segments: list[NarrativeSegment] = []
    if topic:
        intro = f"This analysis examines {topic}."
        segments.append(NarrativeSegment(content=intro, segment_type="intro", order=0))

    for i, frag in enumerate(fragments[:max_segments]):
        text = frag.get("text", "")
        frag_type = frag.get("type", "general")
        if not text.strip():
            continue
        prefix = ""
        if segments:
            prev_type = segments[-1].segment_type
            prefix = add_transition(prev_type, frag_type)
        segments.append(NarrativeSegment(
            content=prefix + text.strip(),
            segment_type=frag_type,
            order=len(segments),
        ))

    if segments:
        conclusion = "In summary, the evidence points to a need for continued investigation."
        segments.append(NarrativeSegment(content=conclusion, segment_type="conclusion", order=len(segments)))

    return segments


def render_narrative(segments: list[NarrativeSegment]) -> str:
    return " ".join(s.content for s in sorted(segments, key=lambda s: s.order))
