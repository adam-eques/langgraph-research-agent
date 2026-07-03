"""Basic example: run the research agent on a query and print the result."""

from __future__ import annotations

from research_agent.streaming import run


def main() -> None:
    query = "What are the key architectural patterns in multi-agent AI systems?"
    print(f"Query: {query}\n{'=' * 60}\n")

    result = run(query)
    final_messages = result.get("messages", [])
    if final_messages:
        print(final_messages[-1].content)
    else:
        print("No output generated.")


if __name__ == "__main__":
    main()
