from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum


class ChunkType(StrEnum):
    FIXED = "fixed"
    SENTENCE = "sentence"
    PARAGRAPH = "paragraph"
    RECURSIVE = "recursive"


@dataclass
class ChunkConfig:
    chunk_type: ChunkType = ChunkType.FIXED
    chunk_size: int = 512
    chunk_overlap: int = 64
    min_chunk_size: int = 50


def fixed_chunk(text: str, config: ChunkConfig) -> list[str]:
    step = max(1, config.chunk_size - config.chunk_overlap)
    chunks = []
    for i in range(0, len(text), step):
        chunk = text[i : i + config.chunk_size]
        if len(chunk) >= config.min_chunk_size:
            chunks.append(chunk)
    return chunks


def sentence_chunk(text: str, config: ChunkConfig) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    chunks: list[str] = []
    current = ""
    for sent in sentences:
        if len(current) + len(sent) + 1 <= config.chunk_size:
            current = (current + " " + sent).strip()
        else:
            if current and len(current) >= config.min_chunk_size:
                chunks.append(current)
            current = sent
    if current and len(current) >= config.min_chunk_size:
        chunks.append(current)
    return chunks


def paragraph_chunk(text: str, config: ChunkConfig) -> list[str]:
    paragraphs = re.split(r"\n{2,}", text.strip())
    return [p.strip() for p in paragraphs if len(p.strip()) >= config.min_chunk_size]


def chunk_text(text: str, config: ChunkConfig) -> list[str]:
    if config.chunk_type == ChunkType.SENTENCE:
        return sentence_chunk(text, config)
    if config.chunk_type == ChunkType.PARAGRAPH:
        return paragraph_chunk(text, config)
    return fixed_chunk(text, config)
