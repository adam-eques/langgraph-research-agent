# Changelog

## [Unreleased]

## [0.2.0] - 2025-09-03

### Added
- Supervisor agent pattern with dynamic routing
- pgvector backend support for production deployments
- LangSmith observability integration
- FastAPI REST and WebSocket streaming endpoints
- Hybrid search (BM25 + semantic) with Reciprocal Rank Fusion
- Cross-encoder reranking with sentence-transformers
- Query decomposition via planner agent
- Fact-checker agent for claim verification
- Conversation memory with Redis backend
- Result caching layer (LRU + Redis)
- Prometheus metrics with no-op fallback
- Batch processing with asyncio concurrency control
- Click CLI: research, index, serve, clear-cache
- Report export: Markdown, HTML, PDF, JSON
- Docker + docker-compose local dev stack
- GitHub Actions CI pipeline

### Changed
- Upgraded to LangGraph 0.2.x API
- Upgraded to LangChain 0.3.x
- Config now supports `MAX_SUPERVISOR_ITERATIONS` and `RETRIEVAL_SCORE_THRESHOLD`

### Fixed
- Retriever now handles empty Chroma collection gracefully
- Streaming correctly yields only synthesizer tokens

## [0.1.0] - 2024-11-12

### Added
- Initial multi-agent pipeline: researcher → analyst → synthesizer
- RAG pipeline: PDF/DOCX/TXT ingestion, Chroma vector store, semantic retrieval
- Tavily web search tool integration
- Sync and async token streaming
- MemorySaver checkpointing
- Basic test suite
