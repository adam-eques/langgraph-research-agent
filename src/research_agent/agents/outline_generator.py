from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class OutlineSection:
    title: str
    level: int
    subsections: list[OutlineSection] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "level": self.level,
            "subsections": [s.to_dict() for s in self.subsections],
        }


def generate_outline(topic: str, subtopics: list[str], depth: int = 2) -> list[OutlineSection]:
    sections = []
    for st in subtopics:
        section = OutlineSection(title=st, level=1)
        if depth > 1:
            sub_keywords = re.findall(r"\b\w{4,}\b", st.lower())
            for kw in sub_keywords[:2]:
                section.subsections.append(
                    OutlineSection(title=f"{kw.capitalize()} details", level=2)
                )
        sections.append(section)
    return sections


def outline_to_markdown(sections: list[OutlineSection], topic: str = "") -> str:
    lines = []
    if topic:
        lines.append(f"# {topic}\n")
    for section in sections:
        prefix = "#" * (section.level + 1)
        lines.append(f"{prefix} {section.title}")
        for sub in section.subsections:
            sub_prefix = "#" * (sub.level + 1)
            lines.append(f"{sub_prefix} {sub.title}")
    return "\n".join(lines)
