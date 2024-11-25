"""Prometheus metrics for the research pipeline.

Gracefully no-ops if prometheus_client is not installed.
"""
from __future__ import annotations

import logging
import time
from contextlib import contextmanager
from typing import Generator

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Attempt to import prometheus_client.  If unavailable, provide no-op stubs
# so the rest of the codebase never has to guard against ImportError.
# ---------------------------------------------------------------------------
try:
    from prometheus_client import (  # type: ignore[import-untyped]
        Counter,
        Gauge,
        Histogram,
        REGISTRY,
    )

    _PROMETHEUS_AVAILABLE = True
except ImportError:
    _PROMETHEUS_AVAILABLE = False
    logger.info(
        "prometheus_client not installed — metrics will be no-ops. "
        "Install with: pip install prometheus-client"
    )

    # -------------------------------------------------------------------
    # Minimal stubs so the rest of the module can import them without error
    # -------------------------------------------------------------------
    class _NoOpMetric:  # type: ignore[no-untyped-def]
        def labels(self, **kwargs):  # noqa: ANN001,ANN201
            return self

        def inc(self, amount: float = 1) -> None: ...
        def dec(self, amount: float = 1) -> None: ...
        def set(self, value: float) -> None: ...
        def observe(self, amount: float) -> None: ...
        def time(self):  # noqa: ANN201
            return self

        def __enter__(self):  # noqa: ANN204
            return self

        def __exit__(self, *args):  # noqa: ANN002,ANN003
            pass

    def Counter(*args, **kwargs):  # type: ignore[misc]  # noqa: N802
        return _NoOpMetric()

    def Gauge(*args, **kwargs):  # type: ignore[misc]  # noqa: N802
        return _NoOpMetric()

    def Histogram(*args, **kwargs):  # type: ignore[misc]  # noqa: N802
        return _NoOpMetric()


# ---------------------------------------------------------------------------
# Metric definitions
# ---------------------------------------------------------------------------

#: Total research requests handled (labels: endpoint)
research_requests_total = Counter(
    "research_requests_total",
    "Total number of research requests received",
    ["endpoint"],
)

#: Total errors encountered (labels: node, error_type)
research_errors_total = Counter(
    "research_errors_total",
    "Total number of errors during research pipeline execution",
    ["node", "error_type"],
)

#: Duration of each pipeline node (labels: node)
research_latency_seconds = Histogram(
    "research_latency_seconds",
    "Wall-clock time spent in each pipeline node (seconds)",
    ["node"],
    buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, float("inf")),
)

#: LLM token usage (labels: model, token_type)
llm_tokens_used = Histogram(
    "llm_tokens_used",
    "Number of tokens consumed per LLM call",
    ["model", "token_type"],
    buckets=(64, 128, 256, 512, 1024, 2048, 4096, 8192, float("inf")),
)

#: Currently active research sessions
active_research_sessions = Gauge(
    "active_research_sessions",
    "Number of research requests currently being processed",
)


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def record_node_latency(node: str, duration: float) -> None:
    """Record the elapsed time for a pipeline node.

    Parameters
    ----------
    node:
        The pipeline node name (e.g. ``"retriever"``, ``"researcher"``).
    duration:
        Wall-clock seconds the node took.
    """
    research_latency_seconds.labels(node=node).observe(duration)


def record_error(node: str, error_type: str) -> None:
    """Increment the error counter for a given node and error type.

    Parameters
    ----------
    node:
        Pipeline node where the error occurred.
    error_type:
        Short error class name or category (e.g. ``"TimeoutError"``).
    """
    research_errors_total.labels(node=node, error_type=error_type).inc()


def record_request(endpoint: str = "research") -> None:
    """Increment the total requests counter.

    Parameters
    ----------
    endpoint:
        API endpoint or entry point name.
    """
    research_requests_total.labels(endpoint=endpoint).inc()


def record_tokens(model: str, input_tokens: int, output_tokens: int) -> None:
    """Record token usage for an LLM call.

    Parameters
    ----------
    model:
        Model identifier (e.g. ``"claude-3-5-sonnet-20241022"``).
    input_tokens:
        Number of prompt tokens consumed.
    output_tokens:
        Number of completion tokens generated.
    """
    llm_tokens_used.labels(model=model, token_type="input").observe(input_tokens)
    llm_tokens_used.labels(model=model, token_type="output").observe(output_tokens)


@contextmanager
def track_session() -> Generator[None, None, None]:
    """Context manager that increments/decrements the active sessions gauge.

    Example
    -------
    >>> with track_session():
    ...     result = run_research_pipeline(query)
    """
    active_research_sessions.inc()
    try:
        yield
    finally:
        active_research_sessions.dec()


@contextmanager
def timed_node(node: str) -> Generator[None, None, None]:
    """Context manager that records wall-clock latency for a named node.

    Example
    -------
    >>> with timed_node("synthesizer"):
    ...     synthesizer_output = synthesizer(state)
    """
    start = time.perf_counter()
    try:
        yield
    except Exception as exc:
        record_error(node=node, error_type=type(exc).__name__)
        raise
    finally:
        record_node_latency(node=node, duration=time.perf_counter() - start)


def is_available() -> bool:
    """Return ``True`` if prometheus_client is installed and metrics are active."""
    return _PROMETHEUS_AVAILABLE
