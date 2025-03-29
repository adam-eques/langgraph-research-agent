from __future__ import annotations

import pytest
from pydantic import ValidationError

from research_agent.schemas import QueryRequest, QueryResponse, BatchQueryRequest


def test_query_request_valid():
    r = QueryRequest(query="What is RAG?")
    assert r.query == "What is RAG?"
    assert r.use_supervisor is False
    assert r.use_rag is True


def test_query_request_too_short():
    with pytest.raises(ValidationError):
        QueryRequest(query="hi")


def test_batch_request_too_large():
    with pytest.raises(ValidationError):
        BatchQueryRequest(queries=["q"] * 60)  # max 50


def test_query_response_defaults():
    r = QueryResponse(query="test", answer="result")
    assert r.citations == []
    assert r.research_notes == []
