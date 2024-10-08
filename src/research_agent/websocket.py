from __future__ import annotations

import asyncio
import json
import logging

from fastapi import WebSocket, WebSocketDisconnect

from research_agent.streaming import astream_tokens

logger = logging.getLogger(__name__)


async def handle_research_ws(websocket: WebSocket) -> None:
    """Handle a WebSocket connection for streaming research results.

    Client sends: {"query": "...", "session_id": "..."}
    Server streams: {"token": "..."} then {"done": true}
    """
    await websocket.accept()
    logger.info("WebSocket connection accepted")
    try:
        while True:
            raw = await websocket.receive_text()
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_json({"error": "Invalid JSON"})
                continue

            query = payload.get("query", "").strip()
            if not query:
                await websocket.send_json({"error": "query is required"})
                continue

            logger.info("WS research query: %.80s", query)
            try:
                async for token in astream_tokens(query):
                    await websocket.send_json({"token": token})
                await websocket.send_json({"done": True})
            except asyncio.CancelledError:
                logger.info("WS stream cancelled by client")
                break
            except Exception as exc:
                logger.error("WS stream error: %s", exc)
                await websocket.send_json({"error": str(exc)})

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
