"""Example: multi-turn research conversation with persistent memory."""
from __future__ import annotations

from research_agent.streaming import run
from research_agent.memory import ConversationMemory

SESSION_ID = "demo-session-001"


def chat(query: str, memory: ConversationMemory) -> str:
    result = run(query)
    messages = result.get("messages", [])
    answer = messages[-1].content if messages else "(no answer)"
    memory.save_turn(SESSION_ID, query, answer)
    return answer


def main() -> None:
    memory = ConversationMemory()

    turns = [
        "What is LangGraph and how does it differ from LangChain?",
        "Can you give me an example of building a supervisor agent with it?",
        "What are the best practices for testing LangGraph pipelines?",
    ]

    for turn in turns:
        print(f"\nYou: {turn}")
        answer = chat(turn, memory)
        print(f"Agent: {answer[:300]}...")

    print(f"\n--- Session history ({SESSION_ID}) ---")
    for h in memory.get_history(SESSION_ID):
        print(f"Q: {h['query'][:60]}...")
        print(f"A: {h['response'][:60]}...")
        print()


if __name__ == "__main__":
    main()
