# RAG Pipeline

## Ingestion

```python
from research_agent.rag.ingestion import ingest, ingest_directory

# Single file
chunks = ingest("report.pdf")

# Entire directory
chunks = ingest_directory("./documents/", recursive=True)
```

Supported formats: `.pdf`, `.docx`, `.txt`, `.md`

Default chunking: `RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)`

### Advanced chunking strategies

```python
from research_agent.rag.chunker import AdvancedChunker

chunker = AdvancedChunker()

# Semantic: respects paragraph/header boundaries
chunks = chunker.semantic_chunk(docs, min_size=200, max_size=1000)

# Sliding window: overlapping windows for dense coverage
chunks = chunker.sliding_window_chunk(docs, size=800, step=400)

# Sentence-aware: groups N sentences per chunk
chunks = chunker.sentence_chunk(docs, sentences_per_chunk=5)
```

## Indexing

```python
from research_agent.rag.retriever import index_document

n = index_document("report.pdf", collection="my_docs")
print(f"Indexed {n} chunks")
```

Vector store backend is controlled by `VECTOR_STORE_BACKEND` env var:
- `chroma` (default): local Chroma with SQLite persistence at `.chroma/`
- `pgvector`: Postgres with pgvector extension — requires `DATABASE_URL`

## Retrieval

```python
from research_agent.rag.retriever import retrieve, format_context

docs = retrieve("What are the key risks?", k=4)
context = format_context(docs)
```

### Hybrid search (BM25 + semantic)

```python
from research_agent.rag.hybrid_search import HybridSearcher

searcher = HybridSearcher(collection="my_docs")
docs = searcher.search("key financial risks", all_docs=corpus, k=4)
```

Uses Reciprocal Rank Fusion (RRF, k=60) to merge BM25 and semantic rankings.

### Reranking

```python
from research_agent.rag.reranker import CrossEncoderReranker

reranker = CrossEncoderReranker()
reranked = reranker.rerank("key risks", docs, top_k=4)
```

### Query expansion

```python
from research_agent.rag.query_expansion import QueryExpander

expander = QueryExpander()
variants = expander.expand("key risks", n=3)
# ["key risks", "main risk factors", "primary concerns", "critical vulnerabilities"]
```

## Post-processing

```python
from research_agent.rag.post_processor import deduplicate, filter_by_score, sort_by_score

docs = deduplicate(docs, threshold=0.9)
docs = filter_by_score(docs, min_score=0.5)
docs = sort_by_score(docs)
```

## Metadata filtering

```python
from research_agent.rag.metadata_filter import MetadataFilter

f = MetadataFilter().where("source", "eq", "report.pdf").where("page", "gt", 5)
filtered = f.apply(docs)
```
