from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class HopQuery:
    query: str
    depends_on: list[int] = field(default_factory=list)
    hop_index: int = 0


@dataclass
class MultiHopPlan:
    original_query: str
    hops: list[HopQuery]
    strategy: str = "sequential"

    def is_parallel(self) -> bool:
        return self.strategy == "parallel"

    def to_dict(self) -> dict:
        return {
            "original": self.original_query,
            "strategy": self.strategy,
            "hops": [
                {"query": h.query, "hop": h.hop_index, "depends_on": h.depends_on}
                for h in self.hops
            ],
        }


_MULTI_PART_PATTERNS = [
    r"\band\s+(?:then|also|additionally|furthermore)\b",
    r"\bfollowed by\b",
    r"\bafter\s+(?:that|which)\b",
    r"\bbased\s+on\s+(?:the|this)\s+(?:answer|result|finding)\b",
]


def needs_multi_hop(query: str) -> bool:
    return any(re.search(p, query, re.I) for p in _MULTI_PART_PATTERNS)


def decompose_query(query: str, max_hops: int = 4) -> MultiHopPlan:
    parts = re.split(r"\s+(?:and then|then|after that|followed by)\s+", query, flags=re.I)
    hops = []
    for i, part in enumerate(parts[:max_hops]):
        deps = [i - 1] if i > 0 else []
        hops.append(HopQuery(query=part.strip(), hop_index=i, depends_on=deps))
    strategy = "parallel" if not needs_multi_hop(query) else "sequential"
    return MultiHopPlan(original_query=query, hops=hops, strategy=strategy)
