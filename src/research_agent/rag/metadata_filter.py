from __future__ import annotations

import logging
from datetime import datetime

from langchain_core.documents import Document

logger = logging.getLogger(__name__)


class MetadataFilter:
    """Filter a list of documents by metadata field conditions."""

    def __init__(self) -> None:
        self._conditions: list[tuple[str, str, object]] = []

    def where(self, field: str, op: str, value: object) -> MetadataFilter:
        """Add a condition. op: 'eq', 'ne', 'gt', 'lt', 'contains', 'in'."""
        self._conditions.append((field, op, value))
        return self

    def apply(self, docs: list[Document]) -> list[Document]:
        results = [d for d in docs if self._matches(d)]
        logger.debug("MetadataFilter: %d -> %d docs", len(docs), len(results))
        return results

    def _matches(self, doc: Document) -> bool:
        for field, op, value in self._conditions:
            actual = doc.metadata.get(field)
            if actual is None:
                return False
            if op == "eq" and actual != value:
                return False
            if op == "ne" and actual == value:
                return False
            if op == "gt" and not (actual > value):  # type: ignore[operator]
                return False
            if op == "lt" and not (actual < value):  # type: ignore[operator]
                return False
            if op == "contains" and value not in str(actual):
                return False
            if op == "in" and actual not in value:  # type: ignore[operator]
                return False
        return True


def filter_by_date(
    docs: list[Document],
    after: datetime | None = None,
    before: datetime | None = None,
    date_field: str = "created_at",
) -> list[Document]:
    """Filter documents by an ISO-8601 date field in metadata."""
    result = []
    for doc in docs:
        raw = doc.metadata.get(date_field)
        if raw is None:
            result.append(doc)
            continue
        try:
            dt = datetime.fromisoformat(str(raw))
            if after and dt < after:
                continue
            if before and dt > before:
                continue
            result.append(doc)
        except ValueError:
            result.append(doc)
    return result
