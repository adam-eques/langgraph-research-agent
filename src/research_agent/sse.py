from __future__ import annotations

import asyncio
import logging
from typing import AsyncIterator

from langchain_core.messages import HumanMessage
from research_agent.state import ResearchState

logger = logging.getLogger(__name__)


async def event_stream(state: ResearchState) -> AsyncIterator[str]:
    """Yield server-sent events from state transitions."""
    yield f"data: query_received: {state['query'][:80]}\n\n"
    if state.get("research_notes"):
        for i, note in enumerate(state["research_notes"], 1):
            yield f"data: note_{i}: {note[:120]}\n\n"
            await asyncio.sleep(0)
    yield "data: done\n\n"
