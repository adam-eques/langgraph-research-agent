"""Example: run evaluation against a small benchmark dataset."""
from __future__ import annotations

import asyncio

DATASET = [
    {
        "query": "What is retrieval-augmented generation?",
        "expected_answer": "RAG combines retrieval from a knowledge base with LLM generation to produce grounded answers.",
        "expected_sources": [],
    },
    {
        "query": "What are the advantages of LangGraph over LangChain Expression Language?",
        "expected_answer": "LangGraph provides explicit state management, conditional routing, and cycle support for agentic workflows.",
        "expected_sources": [],
    },
]


async def main() -> None:
    from research_agent.eval.harness import EvalHarness

    harness = EvalHarness(max_concurrent=2)
    report = await harness.run(DATASET)
    print(report.summary())
    for item in report.items:
        print(f"\nQuery: {item.query}")
        print(f"  Relevance: {item.answer_relevance:.2f} | Faithfulness: {item.faithfulness:.2f}")


if __name__ == "__main__":
    asyncio.run(main())
