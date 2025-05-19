from __future__ import annotations
import logging
from pathlib import Path
from typing import Any
logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf", ".docx"}

def load_text_file(path: str) -> str:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if p.suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {p.suffix}")
    return p.read_text(encoding="utf-8", errors="replace")

def detect_file_type(path: str) -> str:
    suffix = Path(path).suffix.lower()
    return {".pdf": "pdf", ".docx": "docx", ".md": "markdown"}.get(suffix, "text")

def list_documents(directory: str, recursive: bool = False) -> list[str]:
    base = Path(directory)
    if not base.is_dir():
        raise NotADirectoryError(f"Not a directory: {directory}")
    pattern = "**/*" if recursive else "*"
    return [str(p) for p in base.glob(pattern) if p.is_file() and p.suffix in SUPPORTED_EXTENSIONS]
