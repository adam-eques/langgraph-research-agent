from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class SearchConfig:
    strategy: str = "hybrid"
    top_k: int = 5
    rerank: bool = True
    expand_queries: bool = False
    use_rag: bool = True
    use_web: bool = True
    time_filter: str | None = None


def build_search_config(
    query_type: str,
    available_sources: list[str],
    use_rag: bool = True,
) -> SearchConfig:
    base = SearchConfig(use_rag=use_rag)
    if "web" not in available_sources:
        base.use_web = False
    if query_type == "factual":
        base.strategy = "semantic"
        base.top_k = 3
    elif query_type == "comparative":
        base.strategy = "hybrid"
        base.expand_queries = True
        base.top_k = 8
    elif query_type == "procedural":
        base.strategy = "bm25"
        base.rerank = False
    logger.debug("Search config: strategy=%s top_k=%d", base.strategy, base.top_k)
    return base
