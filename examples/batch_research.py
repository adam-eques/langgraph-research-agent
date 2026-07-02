"""Example: run multiple research queries concurrently with BatchProcessor."""

from __future__ import annotations

import asyncio

QUERIES = [
    "What is the current state of large language model research?",
    "How do vector databases compare to traditional databases for AI applications?",
    "What are the best practices for RAG pipeline evaluation?",
]


async def main() -> None:
    from research_agent.batch import BatchProcessor

    processor = BatchProcessor(max_concurrent=3)

    def on_done(completed: int, total: int) -> None:
        print(f"Progress: {completed}/{total}")

    print(f"Running {len(QUERIES)} queries concurrently...\n")
    results = await processor.process_batch(QUERIES, on_complete=on_done)

    for r in results:
        print(f"Query: {r['query'][:60]}...")
        if r.get("error"):
            print(f"  ERROR: {r['error']}")
        else:
            print(f"  Answer: {r.get('answer', '')[:120]}...")
        print()


if __name__ == "__main__":
    asyncio.run(main())
