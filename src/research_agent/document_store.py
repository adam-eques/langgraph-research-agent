from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass
class StoredDocument:
    doc_id: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)

    def matches_tag(self, tag: str) -> bool:
        return tag in self.tags

    def to_dict(self) -> dict:
        return {
            "doc_id": self.doc_id,
            "content": self.content,
            "metadata": self.metadata,
            "tags": self.tags,
            "length": len(self.content),
        }


class DocumentStore:
    def __init__(self) -> None:
        self._docs: dict[str, StoredDocument] = {}

    def add(
        self,
        content: str,
        metadata: dict | None = None,
        tags: list[str] | None = None,
        doc_id: str | None = None,
    ) -> StoredDocument:
        did = doc_id or str(uuid.uuid4())
        doc = StoredDocument(
            doc_id=did,
            content=content,
            metadata=metadata or {},
            tags=tags or [],
        )
        self._docs[did] = doc
        return doc

    def get(self, doc_id: str) -> StoredDocument | None:
        return self._docs.get(doc_id)

    def delete(self, doc_id: str) -> bool:
        return self._docs.pop(doc_id, None) is not None

    def update_metadata(self, doc_id: str, updates: dict) -> bool:
        doc = self._docs.get(doc_id)
        if doc is None:
            return False
        doc.metadata.update(updates)
        return True

    def find_by_tag(self, tag: str) -> list[StoredDocument]:
        return [d for d in self._docs.values() if d.matches_tag(tag)]

    def search_content(self, query: str) -> list[StoredDocument]:
        q = query.lower()
        return [d for d in self._docs.values() if q in d.content.lower()]

    @property
    def count(self) -> int:
        return len(self._docs)

    def all_docs(self) -> list[StoredDocument]:
        return list(self._docs.values())
