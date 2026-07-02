"""Batch processor — runs multiple research queries concurrently with asyncio."""

from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)


class BatchProcessor:
    """Processes a list of research queries concurrently.

    Uses :class:`asyncio.Semaphore` to cap the number of queries running in
    parallel so that downstream LLM / vector-store services are not overwhelmed.

    The processor calls the streaming module's async entry point under the
    hood.  Each query result is returned as a dict regardless of success or
    failure; failed queries carry an ``error`` key instead of ``answer``.

    Example
    -------
    >>> processor = BatchProcessor()
    >>> results = asyncio.run(processor.process_batch(
    ...     ["What is LangGraph?", "Explain RAG architectures"],
    ...     max_concurrent=3,
    ... ))
    >>> for r in results:
    ...     print(r["query"], "->", r.get("error") or r["answer"][:60])
    """

    def __init__(
        self,
        on_complete: Callable[[int, int], None] | None = None,
    ) -> None:
        """
        Parameters
        ----------
        on_complete:
            Optional callback invoked after each query completes.
            Receives ``(completed_count, total_count)``.
        """
        self._on_complete = on_complete

    async def process_batch(
        self,
        queries: list[str],
        max_concurrent: int = 5,
    ) -> list[dict[str, Any]]:
        """Run all queries in *queries* concurrently, capped at *max_concurrent*.

        Parameters
        ----------
        queries:
            Research queries to process.
        max_concurrent:
            Maximum number of queries that may run simultaneously.  If the
            total number of queries is smaller, all run at once.

        Returns
        -------
        list[dict]
            One result dict per query (same order as input).  Each dict has:

            On success::

                {
                    "query": str,
                    "answer": str,
                    "research_notes": list[str],
                    "citations": list[dict],
                    "duration_seconds": float,
                    "error": None,
                }

            On failure::

                {
                    "query": str,
                    "answer": "",
                    "research_notes": [],
                    "citations": [],
                    "duration_seconds": float,
                    "error": str,   # exception message
                }
        """
        if not queries:
            return []

        semaphore = asyncio.Semaphore(max(1, max_concurrent))
        total = len(queries)
        completed_count = 0

        logger.info(
            "BatchProcessor: starting %d queries (max_concurrent=%d)",
            total,
            max_concurrent,
        )

        async def _process_one(query: str, idx: int) -> dict[str, Any]:
            nonlocal completed_count
            async with semaphore:
                start = time.perf_counter()
                result = await self._run_single(query)
                result["duration_seconds"] = round(time.perf_counter() - start, 3)
                completed_count += 1
                logger.info(
                    "BatchProcessor: [%d/%d] done in %.2fs — %s",
                    completed_count,
                    total,
                    result["duration_seconds"],
                    query[:60],
                )
                if self._on_complete is not None:
                    try:
                        self._on_complete(completed_count, total)
                    except Exception:
                        logger.exception("on_complete callback raised an exception")
                return result

        tasks = [_process_one(q, i) for i, q in enumerate(queries)]
        results: list[dict[str, Any]] = await asyncio.gather(*tasks)
        return list(results)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    async def _run_single(self, query: str) -> dict[str, Any]:
        """Execute the research pipeline for a single query.

        Runs the synchronous ``run()`` in a thread pool executor so we do not
        block the event loop.  Returns a normalised result dict.
        """
        # Import here to avoid circular imports at module load time.
        from research_agent.streaming import run as sync_run

        loop = asyncio.get_running_loop()
        try:
            state = await loop.run_in_executor(None, sync_run, query)
            messages = list(state.get("messages", []))
            answer = ""
            for msg in reversed(messages):
                if hasattr(msg, "content") and msg.content:
                    answer = str(msg.content)
                    break

            return {
                "query": query,
                "answer": answer,
                "research_notes": list(state.get("research_notes", [])),
                "citations": list(state.get("citations", [])),
                "error": None,
            }
        except Exception as exc:
            logger.exception("Research pipeline failed for query: %.80s", query)
            return {
                "query": query,
                "answer": "",
                "research_notes": [],
                "citations": [],
                "error": str(exc),
            }
