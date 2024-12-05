# Architecture

## Overview

The research agent is a **multi-agent LangGraph pipeline** that combines web search with document retrieval to answer complex research queries. Agents are independent Python functions that read from and write to a shared `ResearchState` TypedDict, coordinated by a `StateGraph`.

## Agent roles

| Agent | Input | Output | Tools |
|---|---|---|---|
| **Supervisor** | Full state | `next` routing key | None |
| **Retriever** | `query` | `messages`, `citations`, `research_notes` | Chroma / pgvector |
| **Researcher** | `query`, context | `messages` | Tavily search |
| **Web Scraper** | `messages` (URLs) | `messages`, `research_notes` | HTTP fetch |
| **Analyst** | All messages | `research_notes` | None (structured output) |
| **Fact Checker** | `messages`, `citations` | `research_notes` | None |
| **Citation Verifier** | `messages`, `citations` | `research_notes` | None |
| **Synthesizer** | `research_notes`, `messages` | Final `messages` | None |

## State machine

```
┌──────────────────────────────────────────────┐
│               ResearchState                  │
│  messages: list[BaseMessage]                 │
│  query: str                                  │
│  research_notes: list[str]                   │
│  citations: list[Citation]                   │
│  document_context: str                       │
│  next: str                                   │
└──────────────────────────────────────────────┘
```

## Graph modes

### Linear mode (default)
```
retriever → researcher ⇄ research_tools → analyst → synthesizer
```

### Supervisor mode (`use_supervisor=True`)
```
supervisor → [retriever | researcher | analyst | synthesizer] → supervisor → ...
```
The supervisor loops until it decides to output `FINISH`.

## RAG pipeline

1. **Ingestion**: `ingest()` loads PDF/DOCX/TXT → splits with `RecursiveCharacterTextSplitter` (1000 chars, 200 overlap)
2. **Advanced chunking**: optional `AdvancedChunker` for semantic or sliding-window splits
3. **Embedding**: OpenAI `text-embedding-3-small`
4. **Storage**: Chroma (local) or pgvector (Postgres) — switchable via `VECTOR_STORE_BACKEND`
5. **Retrieval**: `retrieve()` with optional hybrid search (BM25 + semantic, RRF fusion)
6. **Reranking**: optional `CrossEncoderReranker` (cross-encoder/ms-marco-MiniLM-L-6-v2)
7. **Post-processing**: `deduplicate()`, `filter_by_score()`, `strip_boilerplate()`

## Streaming

- **Sync**: `stream_tokens(query)` — Python generator, yields synthesizer tokens
- **Async**: `astream_tokens(query)` — async generator for FastAPI SSE and WebSocket
- **WebSocket**: `handle_research_ws()` — bidirectional, supports multiple queries per connection
