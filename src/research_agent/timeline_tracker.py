from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class TimelineEvent:
    timestamp: str
    description: str
    source: str = ""
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "description": self.description,
            "source": self.source,
            "tags": self.tags,
        }


_DATE_PATTERNS = [
    re.compile(r"\b(\d{4}-\d{2}-\d{2})\b"),
    re.compile(
        r"\b(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
        r"Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
        r"\s+(\d{1,2}),?\s+(\d{4})\b",
        re.I,
    ),
    re.compile(r"\bin (\d{4})\b", re.I),
]


def extract_date(text: str) -> str | None:
    for pat in _DATE_PATTERNS:
        m = pat.search(text)
        if m:
            return m.group(0)
    return None


class TimelineTracker:
    def __init__(self) -> None:
        self._events: list[TimelineEvent] = []

    def add_event(
        self,
        timestamp: str,
        description: str,
        source: str = "",
        tags: list[str] | None = None,
    ) -> TimelineEvent:
        event = TimelineEvent(
            timestamp=timestamp,
            description=description,
            source=source,
            tags=tags or [],
        )
        self._events.append(event)
        return event

    def extract_and_add(self, text: str, source: str = "") -> TimelineEvent | None:
        ts = extract_date(text)
        if ts is None:
            return None
        return self.add_event(ts, text[:200], source=source)

    def sorted_events(self) -> list[TimelineEvent]:
        return sorted(self._events, key=lambda e: e.timestamp)

    def filter_by_tag(self, tag: str) -> list[TimelineEvent]:
        return [e for e in self._events if tag in e.tags]

    def filter_by_year(self, year: int) -> list[TimelineEvent]:
        return [e for e in self._events if str(year) in e.timestamp]

    def to_markdown(self) -> str:
        lines = ["# Timeline\n"]
        for e in self.sorted_events():
            lines.append(f"- **{e.timestamp}**: {e.description}")
        return "\n".join(lines)

    @property
    def event_count(self) -> int:
        return len(self._events)
