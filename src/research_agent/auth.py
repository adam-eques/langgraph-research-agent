"""FastAPI middleware for API-key authentication."""
from __future__ import annotations

import logging
import os
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)

# Endpoints that bypass authentication
_PUBLIC_PATHS: frozenset[str] = frozenset({"/health", "/docs", "/openapi.json", "/redoc"})

_API_KEYS_ENV = "API_KEYS"


def _load_keys_from_env() -> set[str]:
    """Read comma-separated API keys from the ``API_KEYS`` environment variable."""
    raw = os.getenv(_API_KEYS_ENV, "")
    keys = {k.strip() for k in raw.split(",") if k.strip()}
    if not keys:
        logger.warning(
            "No API keys configured (API_KEYS env var is empty). "
            "All requests will be rejected unless auth is disabled."
        )
    return keys


class APIKeyMiddleware(BaseHTTPMiddleware):
    """Starlette/FastAPI middleware that enforces X-API-Key header authentication.

    - Returns HTTP 401 when the header is missing or the key is not in *api_keys*.
    - Skips authentication for ``/health``, ``/docs``, ``/openapi.json``, and
      ``/redoc`` so health checks and API documentation remain publicly accessible.
    - When *api_keys* is empty on construction, keys are loaded from the
      ``API_KEYS`` environment variable (comma-separated).

    Example
    -------
    >>> from fastapi import FastAPI
    >>> app = FastAPI()
    >>> app.add_middleware(APIKeyMiddleware, api_keys={"secret-key-1", "secret-key-2"})
    """

    def __init__(
        self,
        app: ASGIApp,
        api_keys: set[str] | None = None,
        public_paths: frozenset[str] | None = None,
    ) -> None:
        super().__init__(app)
        self._api_keys: set[str] = api_keys if api_keys is not None else _load_keys_from_env()
        self._public_paths: frozenset[str] = public_paths if public_paths is not None else _PUBLIC_PATHS

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Allow public / unauthenticated paths
        if request.url.path in self._public_paths:
            return await call_next(request)

        # Extract the API key from the request header
        api_key = request.headers.get("X-API-Key", "").strip()

        if not api_key:
            logger.warning(
                "Rejected request — missing X-API-Key header: %s %s",
                request.method,
                request.url.path,
            )
            return JSONResponse(
                status_code=401,
                content={
                    "detail": "Missing API key. Provide a valid key in the X-API-Key header."
                },
            )

        if api_key not in self._api_keys:
            # Log only the first 4 characters to avoid leaking keys into logs
            logger.warning(
                "Rejected request — invalid API key (%.4s...): %s %s",
                api_key,
                request.method,
                request.url.path,
            )
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid API key."},
            )

        return await call_next(request)


def add_api_key_auth(app: ASGIApp, api_keys: set[str] | None = None) -> None:
    """Convenience helper to add :class:`APIKeyMiddleware` to a FastAPI app.

    Parameters
    ----------
    app:
        The FastAPI application instance.
    api_keys:
        Set of valid API keys.  If ``None``, keys are read from ``API_KEYS``
        env var.
    """
    app.add_middleware(APIKeyMiddleware, api_keys=api_keys)  # type: ignore[attr-defined]
