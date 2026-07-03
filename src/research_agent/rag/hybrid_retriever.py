from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RetrievedDoc:
    content: str
    score: float
    source: str = ""
    metadata: dict | None = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


def reciprocal_rank_fusion(
    dense_results: list[RetrievedDoc],
    sparse_results: list[RetrievedDoc],
    k: int = 60,
) -> list[RetrievedDoc]:
    scores: dict[str, float] = {}
    docs: dict[str, RetrievedDoc] = {}

    for rank, doc in enumerate(dense_results):
        key = doc.content[:80]
        scores[key] = scores.get(key, 0.0) + 1.0 / (k + rank + 1)
        docs[key] = doc

    for rank, doc in enumerate(sparse_results):
        key = doc.content[:80]
        scores[key] = scores.get(key, 0.0) + 1.0 / (k + rank + 1)
        if key not in docs:
            docs[key] = doc

    ranked = sorted(scores.keys(), key=lambda k: scores[k], reverse=True)
    result = []
    for key in ranked:
        d = docs[key]
        result.append(
            RetrievedDoc(
                content=d.content,
                score=scores[key],
                source=d.source,
                metadata=d.metadata,
            )
        )
    return result


class HybridRetriever:
    def __init__(self, k: int = 60, dense_weight: float = 0.6, sparse_weight: float = 0.4) -> None:
        self.k = k
        self.dense_weight = dense_weight
        self.sparse_weight = sparse_weight

    def retrieve(
        self,
        dense: list[RetrievedDoc],
        sparse: list[RetrievedDoc],
        top_k: int = 5,
    ) -> list[RetrievedDoc]:
        fused = reciprocal_rank_fusion(dense, sparse, self.k)
        return fused[:top_k]
