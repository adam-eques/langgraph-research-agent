from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from contextlib import contextmanager


@dataclass
class Span:
    span_id: str
    name: str
    parent_id: str | None
    start_time: float
    end_time: float | None = None
    attributes: dict = field(default_factory=dict)
    status: str = "ok"

    @property
    def duration_ms(self) -> float | None:
        if self.end_time is None:
            return None
        return (self.end_time - self.start_time) * 1000


class SpanTracker:
    def __init__(self) -> None:
        self._spans: list[Span] = []
        self._current_span_id: str | None = None

    def start_span(self, name: str, attributes: dict | None = None) -> Span:
        span = Span(
            span_id=str(uuid.uuid4())[:8],
            name=name,
            parent_id=self._current_span_id,
            start_time=time.monotonic(),
            attributes=attributes or {},
        )
        self._spans.append(span)
        self._current_span_id = span.span_id
        return span

    def end_span(self, span: Span, status: str = "ok") -> None:
        span.end_time = time.monotonic()
        span.status = status
        parent_ids = {s.span_id for s in self._spans}
        candidates = [s for s in self._spans if s.parent_id in parent_ids or s.parent_id is None]
        open_candidates = [s for s in candidates if s.end_time is not None and s.span_id != span.span_id]
        self._current_span_id = open_candidates[-1].span_id if open_candidates else None

    @contextmanager
    def span(self, name: str, attributes: dict | None = None):
        s = self.start_span(name, attributes)
        try:
            yield s
        except Exception as exc:
            s.status = "error"
            s.attributes["error"] = str(exc)
            raise
        finally:
            self.end_span(s)

    def get_spans(self) -> list[Span]:
        return list(self._spans)

    def to_dict(self) -> list[dict]:
        return [
            {
                "span_id": s.span_id,
                "name": s.name,
                "parent_id": s.parent_id,
                "duration_ms": s.duration_ms,
                "status": s.status,
                "attributes": s.attributes,
            }
            for s in self._spans
        ]
