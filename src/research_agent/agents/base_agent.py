from __future__ import annotations
import logging
from typing import Any
from langchain_core.messages import BaseMessage
logger = logging.getLogger(__name__)

class BaseResearchAgent:
    """Abstract base for all research agent nodes."""
    name: str = "base"
    description: str = ""

    def __init__(self, llm=None) -> None:
        self._llm = llm

    def _format_messages(self, state: dict) -> list[BaseMessage]:
        return list(state.get("messages", []))

    def log_start(self, state: dict) -> None:
        query = state.get("query", "")[:60]
        logger.info("Agent %s starting for query: %s", self.name, query)

    def log_done(self, keys_added: list[str]) -> None:
        logger.info("Agent %s completed, added keys: %s", self.name, keys_added)
