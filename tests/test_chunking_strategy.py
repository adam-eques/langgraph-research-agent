from __future__ import annotations
from research_agent.rag.chunking_strategy import (
    chunk_text, ChunkConfig, ChunkType, sentence_chunk, paragraph_chunk,
)


def test_fixed_chunk_count():
    text = "x" * 2000
    config = ChunkConfig(chunk_type=ChunkType.FIXED, chunk_size=200, chunk_overlap=0, min_chunk_size=10)
    chunks = chunk_text(text, config)
    assert len(chunks) == 10


def test_sentence_chunk_splits_correctly():
    text = "AI is powerful. ML is a subset of AI. DL uses neural networks."
    config = ChunkConfig(chunk_type=ChunkType.SENTENCE, chunk_size=40, min_chunk_size=5)
    chunks = sentence_chunk(text, config)
    assert len(chunks) >= 2


def test_paragraph_chunk():
    text = "First paragraph here.\n\nSecond paragraph here.\n\nThird one."
    config = ChunkConfig(chunk_type=ChunkType.PARAGRAPH, min_chunk_size=5)
    chunks = paragraph_chunk(text, config)
    assert len(chunks) == 3


def test_min_chunk_size_filters():
    text = "hi\n\nThis is a longer paragraph that should pass the filter."
    config = ChunkConfig(chunk_type=ChunkType.PARAGRAPH, min_chunk_size=20)
    chunks = paragraph_chunk(text, config)
    assert all(len(c) >= 20 for c in chunks)
