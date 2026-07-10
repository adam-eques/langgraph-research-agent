# langgraph-research-agent

Multi-agent research and document analysis system built with [LangGraph](https://github.com/langchain-ai/langgraph). Combines live web search with a RAG pipeline over indexed documents — coordinated by a supervisor agent that routes work between specialist nodes.

## Architecture

```
                     ┌─────────────┐
                     │  Supervisor │  ← dynamic routing
                     └──────┬──────┘
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
      ┌──────────┐   ┌────────────┐   ┌──────────┐
      │Retriever │   │ Researcher │   │ Analyst  │
      │  (RAG)   │   │(web search)│   │          │
      └──────────┘   └────────────┘   └──────────┘
                                           │
                                           ▼
                                    ┌────────────┐
                                    │Synthesizer │  → final report
                                    └────────────┘
```

**Agents:**
- **Supervisor** — decides which agent acts next based on conversation state; terminates when the answer is complete
- **Retriever** — semantic search over indexed documents (Chroma or pgvector)
- **Researcher** — live web search via [Tavily](https://tavily.com/) with tool-call loop
- **Analyst** — structured analysis of gathered context with Pydantic-validated output
- **Synthesizer** — produces the final cited report; streamed token-by-token

## Features

- LangGraph `StateGraph` with typed state and `add_messages` reducer
- Supervisor pattern with conditional routing between all agent nodes
- RAG pipeline: PDF / DOCX / TXT ingestion → chunking → embedding → semantic retrieval
- Dual vector store backends: **Chroma** (local) and **pgvector** (Postgres), switchable via env var
- Streaming output — sync (`stream_tokens`) and async (`astream_tokens`)
- `MemorySaver` checkpointing for multi-turn conversation persistence
- LangSmith tracing — set `LANGCHAIN_TRACING_V2=true` to enable
- FastAPI REST + streaming endpoint (`GET /research/stream`)
- Structured output with Pydantic schemas throughout (analyst, supervisor)

## Quick start

```bash
git clone https://github.com/adam-eques/langgraph-research-agent
cd langgraph-research-agent
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
cp .env.example .env  # fill in your API keys
```

**Run a research query:**
```bash
python examples/basic_research.py
```

**Index a document and run Q&A:**
```bash
python examples/document_qa.py path/to/report.pdf "What are the key findings?"
```

**Start the API server:**
```bash
pip install fastapi uvicorn
uvicorn research_agent.api:app --reload
# POST /research  {"query": "..."}
# GET  /research/stream?query=...
```

## Configuration

| Variable | Default | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | — | Claude API key (required) |
| `OPENAI_API_KEY` | — | OpenAI key for embeddings |
| `TAVILY_API_KEY` | — | Tavily search key |
| `VECTOR_STORE_BACKEND` | `chroma` | `chroma` or `pgvector` |
| `DATABASE_URL` | — | Postgres URL (pgvector only) |
| `LANGCHAIN_TRACING_V2` | `false` | Enable LangSmith tracing |
| `LANGCHAIN_API_KEY` | — | LangSmith API key |
| `DEFAULT_MODEL` | `claude-3-5-sonnet-20241022` | LLM model override |

## Project structure

```
src/research_agent/
├── graph.py              # StateGraph definition — nodes, edges, routing
├── state.py              # ResearchState TypedDict with Citation support
├── streaming.py          # run(), stream_tokens(), astream_tokens()
├── api.py                # FastAPI REST + streaming endpoint
├── config.py             # Env-based config
├── agents/
│   ├── supervisor.py     # Supervisor with structured routing decisions
│   ├── researcher.py     # Web search agent with tool-call loop
│   ├── retriever_agent.py# RAG-grounded retrieval agent
│   ├── analyst.py        # Structured analysis (Pydantic output)
│   └── synthesizer.py    # Final report generation
├── tools/
│   └── search.py         # Tavily search tool wrapper
└── rag/
    ├── ingestion.py      # Document loading + recursive text splitting
    └── retriever.py      # Chroma / pgvector indexing and retrieval
```

## Running tests

```bash
pytest tests/ -v --cov=research_agent
```

## Tech

LangGraph · LangChain · Anthropic Claude · Tavily · Chroma · pgvector · FastAPI · Pydantic · LangSmith

## License

MIT — see [LICENSE](LICENSE).
