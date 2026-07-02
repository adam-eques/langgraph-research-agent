from __future__ import annotations

import logging

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from research_agent.config import config
from research_agent.state import ResearchState

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """You are an expert analyst. You receive raw research notes and messages \
from the researcher and retriever agents and produce a structured, insightful analysis.

Your output must:
- Identify the core findings and their significance
- Distinguish between web-sourced and document-sourced evidence
- Highlight contradictions or gaps in the research
- Draw connections between disparate data points
- Flag areas that need further investigation
- Assign a confidence level (high/medium/low) to each key claim
"""


class AnalysisOutput(BaseModel):
    summary: str = Field(description="High-level summary of the research findings")
    key_findings: list[str] = Field(description="List of key findings, most important first")
    gaps: list[str] = Field(description="Areas where research is incomplete or uncertain")
    confidence: str = Field(description="Overall confidence level: high, medium, or low")
    next_steps: list[str] = Field(description="Recommended follow-up questions or actions")
    source_breakdown: dict[str, int] = Field(
        default_factory=dict,
        description="Count of evidence by source type: {'web': N, 'documents': N}",
    )


def build_analyst_node():
    llm = ChatAnthropic(
        model=config.default_model,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        api_key=config.anthropic_api_key,
    ).with_structured_output(AnalysisOutput)

    def analyst(state: ResearchState) -> ResearchState:
        conversation = list(state["messages"])
        prompt = [
            SystemMessage(content=_SYSTEM_PROMPT),
            HumanMessage(
                content=f"Research query: {state['query']}\n\nAnalyze the research gathered above."
            ),
        ]
        analysis: AnalysisOutput = llm.invoke(conversation + prompt)

        notes = [
            f"Summary: {analysis.summary}",
            "Key findings:\n" + "\n".join(f"  - {f}" for f in analysis.key_findings),
            "Gaps: " + "; ".join(analysis.gaps),
            f"Confidence: {analysis.confidence}",
            f"Sources: {analysis.source_breakdown}",
        ]
        return {
            "research_notes": notes,
            "next": "synthesizer",
        }

    return analyst
