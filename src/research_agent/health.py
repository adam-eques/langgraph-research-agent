from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)


def check_vector_store() -> dict:
    """Ping the configured vector store and return status."""
    backend = os.getenv("VECTOR_STORE_BACKEND", "chroma")
    try:
        if backend == "pgvector":
            import psycopg

            dsn = os.getenv("DATABASE_URL", "")
            with psycopg.connect(dsn, connect_timeout=3) as conn:
                conn.execute("SELECT 1")
            return {"backend": "pgvector", "status": "ok"}
        else:
            import chromadb

            client = chromadb.PersistentClient(path=".chroma")
            client.list_collections()
            return {"backend": "chroma", "status": "ok"}
    except Exception as exc:
        logger.warning("Vector store health check failed: %s", exc)
        return {"backend": backend, "status": "error", "error": str(exc)}


def check_redis() -> dict:
    """Ping Redis and return status."""
    if os.getenv("MEMORY_BACKEND") != "redis" and os.getenv("CACHE_BACKEND") != "redis":
        return {"status": "not_configured"}
    try:
        import redis

        r = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
        r.ping()
        return {"status": "ok"}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


def check_llm() -> dict:
    """Verify the Anthropic API key is set (does not make a real API call)."""
    key = os.getenv("ANTHROPIC_API_KEY", "")
    if not key:
        return {"status": "missing_key"}
    return {"status": "ok", "key_prefix": key[:8] + "..."}


def full_health() -> dict:
    return {
        "vector_store": check_vector_store(),
        "redis": check_redis(),
        "llm": check_llm(),
    }
