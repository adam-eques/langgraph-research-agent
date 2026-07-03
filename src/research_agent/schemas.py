from __future__ import annotations

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=2000, description="The research question")
    use_supervisor: bool = Field(False, description="Use supervisor agent for dynamic routing")
    use_rag: bool = Field(True, description="Include document retrieval from vector store")
    collection: str = Field("research_docs", description="Vector store collection to query")
    session_id: str | None = Field(None, description="Session ID for conversation memory")


class CitationOut(BaseModel):
    source: str
    excerpt: str
    relevance: str


class QueryResponse(BaseModel):
    query: str
    answer: str
    research_notes: list[str] = []
    citations: list[CitationOut] = []
    session_id: str | None = None


class BatchQueryRequest(BaseModel):
    queries: list[str] = Field(..., min_length=1, max_length=50)
    max_concurrent: int = Field(5, ge=1, le=20)


class BatchQueryResponse(BaseModel):
    results: list[dict]
    total: int
    succeeded: int
    failed: int


class IndexRequest(BaseModel):
    path: str = Field(..., description="File path to index")
    collection: str = Field("research_docs", description="Target collection name")


class IndexResponse(BaseModel):
    path: str
    chunks_indexed: int
    collection: str


class HealthResponse(BaseModel):
    status: str
    version: str = "0.2.0"
    vector_store: str = "chroma"


class EvalItemRequest(BaseModel):
    query: str
    expected_answer: str = ""
    expected_sources: list[str] = []


class EvalReportResponse(BaseModel):
    total: int
    mean_relevance: float
    mean_faithfulness: float
    mean_context_recall: float
    items: list[dict] = []
