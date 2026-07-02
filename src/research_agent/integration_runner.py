from __future__ import annotations

import asyncio
import logging
from typing import Any

logger = logging.getLogger(__name__)


async def run_full_pipeline(
    query: str,
    config: dict | None = None,
    timeout: float = 60.0,
) -> dict[str, Any]:
    """Run the full research pipeline end-to-end with optional timeout."""
    config = config or {}
    try:
        from research_agent.graph import build_graph
        from research_agent.streaming import run

        build_graph(
            checkpointing=config.get("checkpointing", False),
            use_supervisor=config.get("use_supervisor", False),
        )
        result = await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(None, run, query),
            timeout=timeout,
        )
        return result
    except TimeoutError:
        logger.error("Pipeline timed out after %.1fs for query: %s", timeout, query[:80])
        return {"query": query, "answer": "", "error": "timeout"}
    except Exception as exc:
        logger.error("Pipeline error: %s", exc)
        return {"query": query, "answer": "", "error": str(exc)}
