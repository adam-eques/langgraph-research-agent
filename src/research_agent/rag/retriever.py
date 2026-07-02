from __future__ import annotations

import logging
import os
from pathlib import Path

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

from research_agent.config import config
from research_agent.rag.ingestion import ingest

logger = logging.getLogger(__name__)

_PERSIST_DIR = ".chroma"


def _get_embeddings():
    return OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=config.openai_api_key,
    )


def _get_store(collection: str = config.chroma_collection):
    backend = os.getenv("VECTOR_STORE_BACKEND", "chroma")

    if backend == "pgvector":
        from langchain_postgres import PGVector

        return PGVector(
            embeddings=_get_embeddings(),
            collection_name=collection,
            connection=os.getenv("DATABASE_URL", ""),
        )

    from langchain_chroma import Chroma

    return Chroma(
        collection_name=collection,
        embedding_function=_get_embeddings(),
        persist_directory=_PERSIST_DIR,
    )


def index_document(path: str | Path, collection: str = config.chroma_collection) -> int:
    chunks = ingest(path)
    store = _get_store(collection)
    store.add_documents(chunks)
    logger.info("Indexed %d chunks from %s into collection '%s'", len(chunks), path, collection)
    return len(chunks)


def retrieve(
    query: str,
    k: int = config.max_retrieval_results,
    collection: str = config.chroma_collection,
) -> list[Document]:
    store = _get_store(collection)
    results = store.similarity_search(query, k=k)
    logger.info("Retrieved %d documents for query: %.80s", len(results), query)
    return results


def format_context(docs: list[Document]) -> str:
    parts = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("filename", doc.metadata.get("source", "unknown"))
        parts.append(f"[{i}] Source: {source}\n{doc.page_content}")
    return "\n\n---\n\n".join(parts)


def delete_collection(collection: str | None = None) -> None:
    """Drop a Chroma collection and all its indexed documents."""
    target = collection or config.chroma_collection
    store = _get_store(target)
    store.delete_collection()
    logger.info("Deleted collection: %s", target)


def list_collections() -> list[str]:
    """Return names of all Chroma collections in the persist directory."""
    import chromadb

    client = chromadb.PersistentClient(path=_PERSIST_DIR)
    return [c.name for c in client.list_collections()]
