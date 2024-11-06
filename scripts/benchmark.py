"""Benchmark retrieval latency and LLM call latency end-to-end."""
from __future__ import annotations

import argparse
import statistics
import time

QUERIES = [
    "What are the main risks in the current financial report?",
    "Summarize the key performance indicators for Q3.",
    "What regulatory changes affect our business model?",
    "Identify any forward-looking statements in the document.",
    "What is the revenue breakdown by segment?",
]


def benchmark_retrieval(n_runs: int, collection: str) -> dict:
    from research_agent.rag.retriever import retrieve
    latencies = []
    for q in QUERIES[:n_runs]:
        t0 = time.perf_counter()
        retrieve(q, collection=collection)
        latencies.append((time.perf_counter() - t0) * 1000)
    return {
        "mean_ms": statistics.mean(latencies),
        "p95_ms": sorted(latencies)[int(len(latencies) * 0.95)],
        "min_ms": min(latencies),
        "max_ms": max(latencies),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark retrieval and pipeline latency")
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--collection", default="research_docs")
    args = parser.parse_args()

    print(f"Running retrieval benchmark ({args.runs} queries)...")
    stats = benchmark_retrieval(args.runs, args.collection)
    print(f"  mean:  {stats['mean_ms']:.1f}ms")
    print(f"  p95:   {stats['p95_ms']:.1f}ms")
    print(f"  range: {stats['min_ms']:.1f}ms – {stats['max_ms']:.1f}ms")


if __name__ == "__main__":
    main()
