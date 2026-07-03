from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from research_agent import streaming

app = FastAPI(
    title="Research Agent API",
    description="Multi-agent research and document Q&A — LangGraph backend",
    version="0.2.0",
)


class QueryRequest(BaseModel):
    query: str
    use_supervisor: bool = False


class QueryResponse(BaseModel):
    query: str
    answer: str
    research_notes: list[str]


@app.post("/research", response_model=QueryResponse)
async def research(req: QueryRequest) -> QueryResponse:
    result = streaming.run(req.query)
    messages = result.get("messages", [])
    answer = str(messages[-1].content) if messages else ""
    return QueryResponse(
        query=req.query,
        answer=answer,
        research_notes=result.get("research_notes", []),
    )


@app.get("/research/stream")
async def research_stream(query: str):
    async def token_generator():
        async for token in streaming.astream_tokens(query):
            yield token

    return StreamingResponse(token_generator(), media_type="text/plain")


@app.get("/health")
async def health():
    return {"status": "ok"}
