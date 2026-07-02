"""FastAPI integration tests using httpx AsyncClient."""

from __future__ import annotations

from unittest.mock import patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from langchain_core.messages import AIMessage

# ---------------------------------------------------------------------------
# App fixture
# ---------------------------------------------------------------------------


@pytest.fixture
def app():
    from research_agent.api import app as _app

    return _app


@pytest_asyncio.fixture
async def client(app):
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as c:
        yield c


# ---------------------------------------------------------------------------
# /health
# ---------------------------------------------------------------------------


class TestHealthEndpoint:
    @pytest.mark.asyncio
    async def test_health_returns_ok(self, client):
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}

    @pytest.mark.asyncio
    async def test_health_no_auth_needed(self, client):
        # Health endpoint must always be accessible even without API keys
        resp = await client.get("/health")
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# POST /research
# ---------------------------------------------------------------------------


class TestResearchEndpoint:
    @pytest.mark.asyncio
    @patch("research_agent.streaming.run")
    async def test_post_research_returns_answer(self, mock_run, client):
        mock_run.return_value = {
            "messages": [AIMessage(content="LangGraph is a framework for building agents.")],
            "query": "What is LangGraph?",
            "research_notes": ["Note 1"],
            "document_context": "",
            "citations": [],
            "next": "end",
        }

        resp = await client.post("/research", json={"query": "What is LangGraph?"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["query"] == "What is LangGraph?"
        assert "LangGraph" in body["answer"]
        assert isinstance(body["research_notes"], list)

    @pytest.mark.asyncio
    @patch("research_agent.streaming.run")
    async def test_post_research_empty_messages(self, mock_run, client):
        mock_run.return_value = {
            "messages": [],
            "query": "test",
            "research_notes": [],
            "document_context": "",
            "citations": [],
            "next": "",
        }

        resp = await client.post("/research", json={"query": "test"})
        assert resp.status_code == 200
        assert resp.json()["answer"] == ""

    @pytest.mark.asyncio
    async def test_post_research_missing_query_field(self, client):
        resp = await client.post("/research", json={})
        assert resp.status_code == 422  # Unprocessable Entity

    @pytest.mark.asyncio
    @patch("research_agent.streaming.run")
    async def test_post_research_returns_notes(self, mock_run, client):
        mock_run.return_value = {
            "messages": [AIMessage(content="Answer")],
            "query": "q",
            "research_notes": ["Note A", "Note B"],
            "document_context": "",
            "citations": [],
            "next": "end",
        }

        resp = await client.post("/research", json={"query": "q"})
        assert resp.status_code == 200
        assert resp.json()["research_notes"] == ["Note A", "Note B"]


# ---------------------------------------------------------------------------
# GET /research/stream
# ---------------------------------------------------------------------------


class TestStreamEndpoint:
    @pytest.mark.asyncio
    @patch("research_agent.streaming.astream_tokens")
    async def test_stream_yields_tokens(self, mock_astream, client):
        async def _fake_tokens(query):
            yield "Hello"
            yield " world"

        mock_astream.side_effect = _fake_tokens

        resp = await client.get("/research/stream", params={"query": "test"})
        assert resp.status_code == 200
        assert resp.text == "Hello world"

    @pytest.mark.asyncio
    @patch("research_agent.streaming.astream_tokens")
    async def test_stream_empty_response(self, mock_astream, client):
        async def _no_tokens(query):
            return
            yield  # async generator

        mock_astream.side_effect = _no_tokens

        resp = await client.get("/research/stream", params={"query": "empty"})
        assert resp.status_code == 200
        assert resp.text == ""

    @pytest.mark.asyncio
    async def test_stream_missing_query_param(self, client):
        resp = await client.get("/research/stream")
        # FastAPI returns 422 for missing required query params
        assert resp.status_code == 422
