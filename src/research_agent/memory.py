"""Multi-turn conversation memory with in-memory and Redis backends."""
from __future__ import annotations

import json
import logging
import os
import time
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Any

logger = logging.getLogger(__name__)

_BACKEND_ENV = "MEMORY_BACKEND"
_REDIS_URL_ENV = "REDIS_URL"
_DEFAULT_REDIS_URL = "redis://localhost:6379/0"


class _BaseMemoryBackend(ABC):
    """Abstract base for conversation memory backends."""

    @abstractmethod
    def save_turn(self, session_id: str, query: str, response: str) -> None:
        """Persist a single conversation turn."""

    @abstractmethod
    def get_history(self, session_id: str, max_turns: int = 10) -> list[dict[str, Any]]:
        """Retrieve the last *max_turns* turns for a session."""

    @abstractmethod
    def clear(self, session_id: str) -> None:
        """Delete all history for *session_id*."""


class _InMemoryBackend(_BaseMemoryBackend):
    """Simple dict-backed in-process store.  Not suitable for multi-process deployments."""

    def __init__(self) -> None:
        self._store: dict[str, list[dict[str, Any]]] = defaultdict(list)

    def save_turn(self, session_id: str, query: str, response: str) -> None:
        self._store[session_id].append(
            {
                "query": query,
                "response": response,
                "timestamp": time.time(),
            }
        )

    def get_history(self, session_id: str, max_turns: int = 10) -> list[dict[str, Any]]:
        return list(self._store[session_id][-max_turns:])

    def clear(self, session_id: str) -> None:
        self._store.pop(session_id, None)


class _RedisBackend(_BaseMemoryBackend):
    """Redis-backed memory using a JSON list per session key.

    Each session is stored as a Redis list whose elements are JSON-encoded
    turn dicts.  The list is RPUSH'd on save and LRANGE'd on read.
    """

    _KEY_PREFIX = "research_agent:memory:"

    def __init__(self, redis_url: str = _DEFAULT_REDIS_URL) -> None:
        try:
            import redis  # type: ignore[import-untyped]
        except ImportError as exc:
            raise ImportError(
                "redis-py is required for the Redis memory backend. "
                "Install it with: pip install redis"
            ) from exc

        self._client = redis.from_url(redis_url, decode_responses=True)
        logger.info("Redis memory backend connected: %s", redis_url)

    def _key(self, session_id: str) -> str:
        return f"{self._KEY_PREFIX}{session_id}"

    def save_turn(self, session_id: str, query: str, response: str) -> None:
        turn = json.dumps(
            {"query": query, "response": response, "timestamp": time.time()}
        )
        self._client.rpush(self._key(session_id), turn)

    def get_history(self, session_id: str, max_turns: int = 10) -> list[dict[str, Any]]:
        raw = self._client.lrange(self._key(session_id), -max_turns, -1)
        return [json.loads(item) for item in raw]

    def clear(self, session_id: str) -> None:
        self._client.delete(self._key(session_id))


class ConversationMemory:
    """Stores and retrieves multi-turn conversation history.

    The backend is selected via the ``MEMORY_BACKEND`` environment variable:
    - ``memory`` (default): in-process dict, suitable for development/testing
    - ``redis``: Redis-backed, suitable for production / multi-worker deployments

    Example
    -------
    >>> mem = ConversationMemory()
    >>> mem.save_turn("sess-123", "What is RAG?", "RAG stands for ...")
    >>> mem.get_history("sess-123")
    [{'query': 'What is RAG?', 'response': 'RAG stands for ...', 'timestamp': ...}]
    >>> mem.clear("sess-123")
    """

    def __init__(self) -> None:
        backend_name = os.getenv(_BACKEND_ENV, "memory").lower()
        if backend_name == "redis":
            redis_url = os.getenv(_REDIS_URL_ENV, _DEFAULT_REDIS_URL)
            self._backend: _BaseMemoryBackend = _RedisBackend(redis_url)
            logger.info("ConversationMemory: using Redis backend")
        else:
            self._backend = _InMemoryBackend()
            logger.info("ConversationMemory: using in-memory backend")

    def save_turn(self, session_id: str, query: str, response: str) -> None:
        """Persist a conversation turn.

        Parameters
        ----------
        session_id:
            Unique identifier for the conversation session.
        query:
            The user's query for this turn.
        response:
            The assistant's response.
        """
        logger.debug("Saving turn for session %s", session_id)
        self._backend.save_turn(session_id, query, response)

    def get_history(
        self, session_id: str, max_turns: int = 10
    ) -> list[dict[str, Any]]:
        """Retrieve the most recent conversation turns for a session.

        Parameters
        ----------
        session_id:
            The session to retrieve history for.
        max_turns:
            Maximum number of turns to return (most recent first).

        Returns
        -------
        list[dict]
            Each dict has keys ``query``, ``response``, ``timestamp``.
        """
        return self._backend.get_history(session_id, max_turns)

    def clear(self, session_id: str) -> None:
        """Delete all conversation history for *session_id*.

        Parameters
        ----------
        session_id:
            The session whose history should be erased.
        """
        logger.info("Clearing conversation history for session %s", session_id)
        self._backend.clear(session_id)

    def format_as_context(
        self, session_id: str, max_turns: int = 5
    ) -> str:
        """Return conversation history formatted as a context block for prompts.

        Parameters
        ----------
        session_id:
            Session to format.
        max_turns:
            How many recent turns to include.
        """
        history = self.get_history(session_id, max_turns)
        if not history:
            return ""
        lines = []
        for turn in history:
            lines.append(f"User: {turn['query']}")
            lines.append(f"Assistant: {turn['response']}")
        return "\n".join(lines)
