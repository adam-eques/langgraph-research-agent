from __future__ import annotations

import logging
from pathlib import Path

from langchain_core.documents import Document
from research_agent.exceptions import IngestionError
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

_SUPPORTED = {".pdf", ".docx", ".txt", ".md"}

_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", ". ", " ", ""],
)


def load_document(path: str | Path) -> list[Document]:
    path = Path(path)
    if path.suffix not in _SUPPORTED:
        raise ValueError(f"Unsupported file type: {path.suffix}. Supported: {_SUPPORTED}")

    logger.info("Loading document: %s", path)

    if path.suffix == ".pdf":
        loader = PyPDFLoader(str(path))
    elif path.suffix == ".docx":
        loader = Docx2txtLoader(str(path))
    else:
        loader = TextLoader(str(path), encoding="utf-8")

    docs = loader.load()
    for doc in docs:
        doc.metadata["source"] = str(path)
        doc.metadata["filename"] = path.name

    return docs


def split_documents(docs: list[Document]) -> list[Document]:
    chunks = _splitter.split_documents(docs)
    logger.info("Split %d documents into %d chunks", len(docs), len(chunks))
    return chunks


def ingest(path: str | Path) -> list[Document]:
    docs = load_document(path)
    return split_documents(docs)


def ingest_directory(directory: str, recursive: bool = False) -> list:
    """Ingest all supported documents from a directory."""
    from pathlib import Path
    p = Path(directory)
    pattern = "**/*" if recursive else "*"
    docs = []
    for path in p.glob(pattern):
        if path.suffix in {".pdf", ".docx", ".txt", ".md"} and path.is_file():
            try:
                docs.extend(ingest(path))
                logger.info("Ingested: %s", path.name)
            except Exception as exc:
                logger.warning("Skipping %s: %s", path.name, exc)
    return docs
