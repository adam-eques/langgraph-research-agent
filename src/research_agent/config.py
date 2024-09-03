from __future__ import annotations

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    tavily_api_key: str = os.getenv("TAVILY_API_KEY", "")

    default_model: str = os.getenv("DEFAULT_MODEL", "claude-3-5-sonnet-20241022")
    temperature: float = float(os.getenv("TEMPERATURE", "0"))
    max_tokens: int = int(os.getenv("MAX_TOKENS", "4096"))

    chroma_host: str = os.getenv("CHROMA_HOST", "localhost")
    chroma_port: int = int(os.getenv("CHROMA_PORT", "8000"))
    chroma_collection: str = os.getenv("CHROMA_COLLECTION", "research_docs")

    max_search_results: int = int(os.getenv("MAX_SEARCH_RESULTS", "5"))
    max_retrieval_results: int = int(os.getenv("MAX_RETRIEVAL_RESULTS", "4"))

    langchain_tracing: bool = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
    langchain_project: str = os.getenv("LANGCHAIN_PROJECT", "research-agent")


config = Config()
