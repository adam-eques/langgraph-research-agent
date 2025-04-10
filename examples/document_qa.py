"""Example: index a document then run Q&A against it."""
from __future__ import annotations

import sys
from pathlib import Path

from research_agent.rag.retriever import index_document
from research_agent.streaming import run, stream_tokens


def main(doc_path: str, query: str) -> None:
    path = Path(doc_path)
    if not path.exists():
        print(f"File not found: {path}")
        sys.exit(1)

    print(f"Indexing: {path.name}...")
    n_chunks = index_document(path)
    print(f"Indexed {n_chunks} chunks.\n")

    print(f"Query: {query}\n{'=' * 60}\n")
    for token in stream_tokens(query):
        print(token, end="", flush=True)
    print()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python document_qa.py <path/to/document.pdf> \"your question\"")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
