from __future__ import annotations

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from research_agent.config import config
from research_agent.state import ResearchState

_SYSTEM_PROMPT = """You are a synthesis specialist. You receive analyzed research notes and \
produce a clear, concise, well-structured final report for the end user.

Guidelines:
- Write for clarity — the user may not be an expert in the topic
- Structure your response with clear sections
- Back every claim with evidence from the research
- Keep the tone professional and objective
- End with a brief "Bottom Line" section
"""


def build_synthesizer_node():
    llm = ChatAnthropic(
        model=config.default_model,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        api_key=config.anthropic_api_key,
    )

    def synthesizer(state: ResearchState) -> ResearchState:
        notes_block = "\n\n".join(state.get("research_notes", []))
        messages = [
            SystemMessage(content=_SYSTEM_PROMPT),
            HumanMessage(content=(
                f"Original query: {state['query']}\n\n"
                f"Research analysis:\n{notes_block}\n\n"
                "Produce the final report."
            )),
        ]
        response: AIMessage = llm.invoke(messages)
        return {
            "messages": [response],
            "next": "end",
        }

    return synthesizer
