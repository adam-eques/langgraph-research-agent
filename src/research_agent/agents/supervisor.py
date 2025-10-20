from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage

from research_agent.config import config
from research_agent.state import ResearchState

_MEMBERS = ["retriever", "researcher", "analyst", "synthesizer"]

_SYSTEM_PROMPT = f"""You are a research supervisor coordinating a team of specialist agents:

- retriever: searches the local document knowledge base for relevant context
- researcher: performs live web search to gather current information
- analyst: synthesizes gathered information into structured findings
- synthesizer: produces the final, user-facing report

Given the conversation so far and the original query, decide which agent should act next.
Respond with ONLY the agent name. When the report is complete, respond with "FINISH".

Available agents: {', '.join(_MEMBERS)}
"""

NextAgent = Literal["retriever", "researcher", "analyst", "synthesizer", "FINISH"]


class SupervisorDecision(BaseModel):
    next: NextAgent = Field(description="The next agent to run, or FINISH when done")
    reasoning: str = Field(description="Brief reason for this routing decision")


def build_supervisor_node():
    llm = ChatAnthropic(
        model=config.default_model,
        temperature=0,
        max_tokens=256,
        api_key=config.anthropic_api_key,
    ).with_structured_output(SupervisorDecision)

    def supervisor(state: ResearchState) -> ResearchState:
        messages = [
            SystemMessage(content=_SYSTEM_PROMPT),
            HumanMessage(content=f"Query: {state['query']}\n\nDecide the next agent."),
        ] + list(state["messages"])

        decision: SupervisorDecision = llm.invoke(messages)
        next_node = "end" if decision.next == "FINISH" else decision.next
        return {"next": next_node}

    def route(state: ResearchState) -> str:
        return state.get("next", "end")

    return supervisor, route
