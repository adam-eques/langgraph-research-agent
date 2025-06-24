#!/usr/bin/env python3
"""Demo: running the research graph with use_supervisor=True.

In supervisor mode, a dedicated LLM-powered supervisor node dynamically
decides which agent to call next based on the current conversation state.
This enables more flexible, multi-pass research workflows compared to the
fixed retriever → researcher → analyst → synthesizer chain.

Run from the repo root:

    python examples/supervisor_mode.py

Requirements:
    ANTHROPIC_API_KEY must be set in the environment (or .env file).
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

# Add src/ to the path when running as a standalone script.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from research_agent.logging_config import setup_logging

setup_logging(level="INFO")

import logging

from langchain_core.messages import BaseMessage

from research_agent.graph import build_graph
from research_agent.state import ResearchState

logger = logging.getLogger(__name__)


def run_with_supervisor(query: str) -> dict:
    """Run the research pipeline with the supervisor agent enabled.

    The supervisor observes the conversation at each step and decides which
    specialised agent (retriever, researcher, analyst, synthesizer) to invoke
    next.  It can revisit agents multiple times and will emit ``FINISH`` when
    it determines the report is complete.

    Parameters
    ----------
    query:
        The research question to answer.

    Returns
    -------
    dict
        The final pipeline state.
    """
    print(f"\n{'='*60}")
    print(f"Research query: {query}")
    print(f"Mode: SUPERVISOR (dynamic routing)")
    print(f"{'='*60}\n")

    graph = build_graph(
        checkpointing=False,
        use_supervisor=True,
    )

    initial: ResearchState = {
        "messages": [],
        "query": query,
        "research_notes": [],
        "document_context": "",
        "citations": [],
        "next": "",
    }

    start = time.perf_counter()

    # Stream events so we can observe each supervisor decision.
    step_count = 0
    final_state: ResearchState = initial

    print("Supervisor decisions:\n")
    for event in graph.stream(initial, stream_mode="values"):
        step_count += 1
        next_node = event.get("next", "")
        messages: list[BaseMessage] = list(event.get("messages", []))
        last_msg = messages[-1].content[:80] if messages else "(no message)"

        if next_node:
            print(f"  [{step_count:02d}] next={next_node!r:15s}  last_msg={last_msg!r}")

        final_state = event

    elapsed = time.perf_counter() - start
    print(f"\nCompleted in {elapsed:.1f}s over {step_count} steps\n")
    return final_state


def print_result(state: ResearchState) -> None:
    """Print the final research answer and key metrics."""
    messages = list(state.get("messages", []))
    answer = ""
    for msg in reversed(messages):
        if hasattr(msg, "content") and msg.content:
            answer = str(msg.content)
            break

    notes = state.get("research_notes", [])
    citations = state.get("citations", [])

    print("=" * 60)
    print("FINAL ANSWER")
    print("=" * 60)
    print(answer or "(no answer generated)")

    if notes:
        print(f"\n{'─'*40}")
        print(f"Research notes ({len(notes)}):")
        for note in notes[:3]:
            print(f"  • {note[:120]}")

    if citations:
        print(f"\n{'─'*40}")
        print(f"Citations ({len(citations)}):")
        for i, cite in enumerate(citations[:3], 1):
            print(f"  [{i}] {cite.get('source', 'unknown')} — {cite.get('excerpt', '')[:60]}")

    print()


def compare_modes(query: str) -> None:
    """Compare supervisor vs. linear pipeline on the same query (informational)."""
    print("\nNote: To compare supervisor vs. linear mode, run:")
    print(f"  python -c \"from research_agent.streaming import run; result = run({query!r}); print(result)\"")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Research agent supervisor mode demo")
    parser.add_argument(
        "query",
        nargs="?",
        default="What are the key architectural differences between GPT-4 and Claude 3, and how do they impact performance on reasoning tasks?",
        help="Research question to answer (default: GPT-4 vs Claude architecture comparison)",
    )
    parser.add_argument(
        "--stream-only",
        action="store_true",
        help="Use streaming instead of event-by-event observation",
    )
    args = parser.parse_args()

    if args.stream_only:
        # Alternative: use the simple streaming API
        from research_agent.streaming import stream_tokens

        print(f"Streaming answer for: {args.query}\n")
        for token in stream_tokens(args.query):
            print(token, end="", flush=True)
        print()
    else:
        final_state = run_with_supervisor(args.query)
        print_result(final_state)
        compare_modes(args.query)
