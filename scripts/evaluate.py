"""Run the evaluation harness against a JSONL dataset file."""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path


def load_dataset(path: str) -> list[dict]:
    items = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    if not items:
        print(f"ERROR: dataset at {path!r} is empty")
        sys.exit(1)
    return items


async def _run(dataset_path: str, output_path: str | None, concurrency: int) -> None:
    from research_agent.eval.harness import EvalHarness

    dataset = load_dataset(dataset_path)
    print(f"Loaded {len(dataset)} eval items from {dataset_path}")

    harness = EvalHarness(max_concurrent=concurrency)
    report = await harness.run(dataset)

    print(report.summary())

    if output_path:
        Path(output_path).write_text(report.model_dump_json(indent=2))
        print(f"Report saved to {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run eval harness on a JSONL dataset")
    parser.add_argument("dataset", help="Path to .jsonl dataset file")
    parser.add_argument("--output", "-o", help="Save JSON report to this path")
    parser.add_argument("--concurrency", "-c", type=int, default=3)
    args = parser.parse_args()
    asyncio.run(_run(args.dataset, args.output, args.concurrency))


if __name__ == "__main__":
    main()
