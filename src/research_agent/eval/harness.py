"""Evaluation harness — runs the research pipeline on a dataset and collects metrics."""

from __future__ import annotations

import asyncio
import logging
import statistics
import time
from typing import Any

from pydantic import BaseModel, Field

from research_agent.eval.metrics import answer_relevance, context_recall, f1_score, faithfulness

logger = logging.getLogger(__name__)


class ItemScore(BaseModel):
    """Per-item evaluation scores."""

    query: str
    expected_answer: str
    generated_answer: str
    answer_relevance: float = Field(ge=0.0, le=1.0)
    faithfulness: float = Field(ge=0.0, le=1.0)
    context_recall: float = Field(ge=0.0, le=1.0)
    f1: float = Field(ge=0.0, le=1.0)
    latency_seconds: float
    error: str | None = None


class EvalReport(BaseModel):
    """Aggregate evaluation report for a full dataset run."""

    total_items: int
    successful_items: int
    failed_items: int
    mean_answer_relevance: float
    mean_faithfulness: float
    mean_context_recall: float
    mean_f1: float
    mean_latency_seconds: float
    scores: list[ItemScore]

    def summary(self) -> str:
        """Return a human-readable one-paragraph summary of the report."""
        return (
            f"Evaluated {self.total_items} items "
            f"({self.successful_items} successful, {self.failed_items} failed).\n"
            f"  Answer relevance:  {self.mean_answer_relevance:.3f}\n"
            f"  Faithfulness:      {self.mean_faithfulness:.3f}\n"
            f"  Context recall:    {self.mean_context_recall:.3f}\n"
            f"  Token F1:          {self.mean_f1:.3f}\n"
            f"  Latency (mean):    {self.mean_latency_seconds:.2f}s"
        )


class EvalHarness:
    """Runs the full research pipeline on a dataset and collects evaluation metrics.

    Each dataset item must be a dict with keys:
    - ``query`` (str): the research question
    - ``expected_answer`` (str): ground-truth reference answer
    - ``expected_sources`` (list[str]): expected source names or passages

    Example
    -------
    >>> dataset = [
    ...     {
    ...         "query": "What is RAG?",
    ...         "expected_answer": "Retrieval Augmented Generation combines ...",
    ...         "expected_sources": ["attention_is_all_you_need.pdf"],
    ...     }
    ... ]
    >>> harness = EvalHarness()
    >>> report = harness.run(dataset)
    >>> print(report.summary())
    """

    def __init__(self, max_concurrent: int = 3) -> None:
        self._max_concurrent = max_concurrent

    def run(
        self,
        dataset: list[dict[str, Any]],
        use_langsmith: bool = True,
    ) -> EvalReport:
        """Execute the pipeline on all items in *dataset* and return an EvalReport.

        Parameters
        ----------
        dataset:
            List of evaluation items (see class docstring for schema).
        use_langsmith:
            When ``True`` and LangSmith tracing is configured, traces are
            automatically uploaded under the project ``research-agent-eval``.

        Returns
        -------
        EvalReport
            Aggregated and per-item scores.
        """
        if use_langsmith:
            self._configure_langsmith()

        logger.info(
            "EvalHarness: running %d items (max_concurrent=%d)", len(dataset), self._max_concurrent
        )

        try:
            loop = asyncio.get_running_loop()
            scores = loop.run_until_complete(self._run_all(dataset))
        except RuntimeError:
            scores = asyncio.run(self._run_all(dataset))

        return self._build_report(scores)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    async def _run_all(self, dataset: list[dict[str, Any]]) -> list[ItemScore]:
        semaphore = asyncio.Semaphore(self._max_concurrent)

        async def _eval_one(item: dict[str, Any]) -> ItemScore:
            async with semaphore:
                return await asyncio.get_running_loop().run_in_executor(None, self._eval_item, item)

        tasks = [_eval_one(item) for item in dataset]
        return list(await asyncio.gather(*tasks))

    def _eval_item(self, item: dict[str, Any]) -> ItemScore:
        from research_agent.streaming import run as sync_run

        query: str = item["query"]
        expected_answer: str = item.get("expected_answer", "")
        expected_sources: list[str] = item.get("expected_sources", [])

        start = time.perf_counter()
        try:
            state = sync_run(query)
            messages = list(state.get("messages", []))
            generated = ""
            for msg in reversed(messages):
                if hasattr(msg, "content") and msg.content:
                    generated = str(msg.content)
                    break

            research_notes: list[str] = list(state.get("research_notes", []))
            context_passages = research_notes + list(
                state.get("document_context", "").split("\n\n")
            )
            latency = time.perf_counter() - start

            rel = answer_relevance(query, generated)
            faith = faithfulness(generated, "\n".join(context_passages[:5]))
            recall = context_recall(expected_answer, expected_sources or context_passages[:3])
            f1 = f1_score(generated, expected_answer)

            return ItemScore(
                query=query,
                expected_answer=expected_answer,
                generated_answer=generated,
                answer_relevance=rel,
                faithfulness=faith,
                context_recall=recall,
                f1=f1,
                latency_seconds=round(latency, 3),
                error=None,
            )
        except Exception as exc:
            latency = time.perf_counter() - start
            logger.exception("EvalHarness: pipeline failed for query: %.80s", query)
            return ItemScore(
                query=query,
                expected_answer=expected_answer,
                generated_answer="",
                answer_relevance=0.0,
                faithfulness=0.0,
                context_recall=0.0,
                f1=0.0,
                latency_seconds=round(latency, 3),
                error=str(exc),
            )

    @staticmethod
    def _build_report(scores: list[ItemScore]) -> EvalReport:
        successful = [s for s in scores if s.error is None]
        failed = [s for s in scores if s.error is not None]

        def _mean(values: list[float]) -> float:
            return statistics.mean(values) if values else 0.0

        return EvalReport(
            total_items=len(scores),
            successful_items=len(successful),
            failed_items=len(failed),
            mean_answer_relevance=_mean([s.answer_relevance for s in successful]),
            mean_faithfulness=_mean([s.faithfulness for s in successful]),
            mean_context_recall=_mean([s.context_recall for s in successful]),
            mean_f1=_mean([s.f1 for s in successful]),
            mean_latency_seconds=_mean([s.latency_seconds for s in scores]),
            scores=scores,
        )

    @staticmethod
    def _configure_langsmith() -> None:
        """Enable LangSmith tracing for the evaluation run if configured."""
        import os

        if (
            os.getenv("LANGCHAIN_API_KEY")
            and os.getenv("LANGCHAIN_TRACING_V2", "").lower() == "true"
        ):
            os.environ.setdefault("LANGCHAIN_PROJECT", "research-agent-eval")
            logger.info("LangSmith tracing enabled for eval run")
        else:
            logger.debug("LangSmith not configured — skipping tracing")
