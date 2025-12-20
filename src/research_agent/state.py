from __future__ import annotations

from typing import Annotated, Sequence
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class Citation(TypedDict):
    source: str
    excerpt: str
    relevance: str


class ResearchState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    query: str
    research_notes: list[str]
    document_context: str
    citations: list[Citation]
    next: str
