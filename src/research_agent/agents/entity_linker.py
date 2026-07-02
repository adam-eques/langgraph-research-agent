from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class LinkedEntity:
    text: str
    entity_type: str
    canonical: str
    confidence: float
    start: int
    end: int


_ENTITY_PATTERNS = {
    "ORGANIZATION": [
        r"\b(Google|OpenAI|Anthropic|Meta|Microsoft|Amazon|Apple|NVIDIA|DeepMind)\b",
        r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Inc|Corp|Ltd|LLC|GmbH|AG))\b",
    ],
    "TECHNOLOGY": [
        r"\b(LangGraph|LangChain|PyTorch|TensorFlow|ChromaDB|Pinecone|Weaviate)\b",
        r"\b(GPT-[34]-?\d*|Claude-?\d*|Gemini|Llama-?\d*)\b",
    ],
    "CONCEPT": [
        r"\b(RAG|LLM|NLP|ML|AI|DL|RL|GANs?|Transformers?|BERT|GPT)\b",
    ],
}


def link_entities(text: str) -> list[LinkedEntity]:
    entities: list[LinkedEntity] = []
    for etype, patterns in _ENTITY_PATTERNS.items():
        for pattern in patterns:
            for m in re.finditer(pattern, text):
                entities.append(
                    LinkedEntity(
                        text=m.group(0),
                        entity_type=etype,
                        canonical=m.group(0).strip(),
                        confidence=0.8,
                        start=m.start(),
                        end=m.end(),
                    )
                )
    entities.sort(key=lambda e: e.start)
    return entities


def group_by_type(entities: list[LinkedEntity]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for e in entities:
        result.setdefault(e.entity_type, []).append(e.canonical)
    return {k: list(dict.fromkeys(v)) for k, v in result.items()}
