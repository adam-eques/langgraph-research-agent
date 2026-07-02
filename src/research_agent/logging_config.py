"""Structured JSON logging setup for the research_agent package."""

from __future__ import annotations

import json
import logging
import logging.config
import sys
import time
from typing import Any


class _JsonFormatter(logging.Formatter):
    """Formats log records as newline-delimited JSON.

    Each line is a self-contained JSON object with at minimum:
    ``timestamp``, ``level``, ``logger``, ``message``.

    Optional fields added when present:
    - ``exc_info``  — formatted exception traceback
    - ``request_id`` — thread-local or record extra for distributed tracing
    - any extra fields injected via ``logging.LogRecord`` kwargs
    """

    _RESERVED = frozenset(
        {
            "args",
            "asctime",
            "created",
            "exc_info",
            "exc_text",
            "filename",
            "funcName",
            "levelname",
            "levelno",
            "lineno",
            "message",
            "module",
            "msecs",
            "msg",
            "name",
            "pathname",
            "process",
            "processName",
            "relativeCreated",
            "stack_info",
            "thread",
            "threadName",
        }
    )

    def format(self, record: logging.LogRecord) -> str:
        record.message = record.getMessage()
        payload: dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.message,
            "module": record.module,
            "func": record.funcName,
            "line": record.lineno,
        }

        # Include request_id if present (added by middleware or context var)
        request_id = getattr(record, "request_id", None)
        if request_id:
            payload["request_id"] = request_id

        # Include exception info
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)

        # Include stack info
        if record.stack_info:
            payload["stack_info"] = self.formatStack(record.stack_info)

        # Pass through any extra fields not in the reserved set
        for key, value in record.__dict__.items():
            if key not in self._RESERVED and not key.startswith("_"):
                try:
                    json.dumps(value)  # only include JSON-serialisable extras
                    payload[key] = value
                except (TypeError, ValueError):
                    payload[key] = str(value)

        return json.dumps(payload, default=str)

    def formatTime(self, record: logging.LogRecord, datefmt: str | None = None) -> str:  # noqa: N802
        # ISO 8601 with milliseconds
        ct = time.gmtime(record.created)
        t = time.strftime("%Y-%m-%dT%H:%M:%S", ct)
        return f"{t}.{int(record.msecs):03d}Z"


class _RequestIdFilter(logging.Filter):
    """Injects a ``request_id`` attribute into every log record.

    When no request context is active the attribute is set to an empty string.
    Call :func:`set_request_id` from middleware to populate it.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "request_id"):
            record.request_id = _current_request_id()
        return True


# Module-level storage for current request ID.
# In a real async app this would be a contextvars.ContextVar.
_REQUEST_ID: str = ""


def set_request_id(request_id: str) -> None:
    """Set the active request ID (called from FastAPI middleware)."""
    global _REQUEST_ID
    _REQUEST_ID = request_id


def get_request_id() -> str:
    """Return the active request ID, or empty string if none is set."""
    return _REQUEST_ID


def _current_request_id() -> str:
    return _REQUEST_ID


def setup_logging(
    level: str = "INFO",
    json_output: bool = False,
    logger_name: str = "research_agent",
) -> None:
    """Configure structured logging for the research_agent package.

    Parameters
    ----------
    level:
        Logging level name (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    json_output:
        When ``True`` emit newline-delimited JSON; when ``False`` use a human-
        readable coloured format suitable for development.
    logger_name:
        Root logger name to configure.  Defaults to ``"research_agent"`` so
        only our package loggers are affected.

    Example
    -------
    >>> from research_agent.logging_config import setup_logging
    >>> setup_logging(level="DEBUG", json_output=True)
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(_RequestIdFilter())

    if json_output:
        handler.setFormatter(_JsonFormatter())
    else:
        fmt = "%(asctime)s | %(levelname)-8s | %(name)-30s | %(funcName)s:%(lineno)d | %(message)s"
        handler.setFormatter(logging.Formatter(fmt, datefmt="%H:%M:%S"))

    root = logging.getLogger(logger_name)
    root.setLevel(numeric_level)
    root.handlers.clear()
    root.addHandler(handler)
    root.propagate = False

    # Also quieten noisy third-party loggers at WARNING level.
    for noisy in ("httpx", "httpcore", "chromadb", "urllib3", "openai"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    root.debug(
        "Logging configured: level=%s, json=%s",
        level.upper(),
        json_output,
    )
