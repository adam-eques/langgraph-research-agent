"""Fact-checker agent — verifies each key claim in the synthesiser output."""
from __future__ import annotations

import logging
from typing import Any

from pydantic import BaseModel, Field
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage

from research_agent.config import config
from research_agent.state import ResearchState

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """You are a rigorous fact-checker. You will be given:
1. A synthesised research answer
2. The raw research notes that were used to produce it

Your task is to verify each key factual claim in the answer against the research notes.

For every claim you identify:
- verdict: SUPPORTED | UNSUPPORTED | PARTIALLY_SUPPORTED | UNVERIFIABLE
- confidence: 0.0–1.0 (how certain you are of your verdict)
- evidence: the specific snippet from research notes that supports or refutes the claim

Then give an overall_verdict for the whole answer:
- VERIFIED: all major claims are supported
- MOSTLY_VERIFIED: minor unsupported details, core claims hold
- MIXED: significant unsupported claims alongside supported ones
- UNRELIABLE: majority of claims lack supporting evidence

Be precise and fair. Acknowledge when notes are incomplete rather than marking good-faith \
inferences as unsupported.
"""


class ClaimVerdict(BaseModel):
    """Verdict on a single factual claim."""

    claim: str = Field(description="The exact claim from the answer being verified")
    verdict: str = Field(
        description="SUPPORTED | UNSUPPORTED | PARTIALLY_SUPPORTED | UNVERIFIABLE"
    )
    confidence: float = Field(
        description="Confidence in the verdict, 0.0–1.0",
        ge=0.0,
        le=1.0,
    )
    evidence: str = Field(
        description="The research note excerpt supporting or refuting this claim"
    )


class FactCheckResult(BaseModel):
    """Complete fact-check results for a synthesised answer."""

    claims: list[ClaimVerdict] = Field(
        description="Individual claim verdicts, ordered as they appear in the answer"
    )
    overall_verdict: str = Field(
        description="VERIFIED | MOSTLY_VERIFIED | MIXED | UNRELIABLE"
    )
    summary: str = Field(
        description="Brief human-readable summary of the fact-check findings"
    )
    unsupported_count: int = Field(
        description="Number of claims that are UNSUPPORTED or UNVERIFIABLE"
    )

    @property
    def support_rate(self) -> float:
        """Fraction of claims that are SUPPORTED (0–1)."""
        if not self.claims:
            return 1.0
        supported = sum(
            1 for c in self.claims if c.verdict in ("SUPPORTED", "PARTIALLY_SUPPORTED")
        )
        return supported / len(self.claims)


class FactCheckerAgent:
    """Verifies synthesised answers against research notes.

    Used as an optional post-synthesis quality gate.  When injected into the
    graph the result is stored in the state so the API can expose it and the
    synthesiser can optionally revise its output.

    Example
    -------
    >>> checker = FactCheckerAgent()
    >>> result = checker.check(answer="The population of France is 70 million.",
    ...                        research_notes=["France population: ~68M (INSEE 2023)"])
    >>> result.overall_verdict
    'PARTIALLY_VERIFIED'
    """

    def __init__(self) -> None:
        self._llm = ChatAnthropic(
            model=config.default_model,
            temperature=0,
            max_tokens=2048,
            api_key=config.anthropic_api_key,
        ).with_structured_output(FactCheckResult)

    def check(self, answer: str, research_notes: list[str]) -> FactCheckResult:
        """Verify claims in *answer* against *research_notes*.

        Parameters
        ----------
        answer:
            The synthesised answer to fact-check.
        research_notes:
            Raw research notes collected by the researcher/analyst nodes.

        Returns
        -------
        FactCheckResult
            Structured verdicts for each claim plus an overall verdict.
        """
        if not answer.strip():
            logger.warning("fact_checker received empty answer — skipping")
            return FactCheckResult(
                claims=[],
                overall_verdict="UNVERIFIABLE",
                summary="No answer was provided to fact-check.",
                unsupported_count=0,
            )

        notes_block = "\n\n".join(research_notes) if research_notes else "(no research notes)"
        logger.info("Fact-checking answer (%d chars) against %d notes", len(answer), len(research_notes))

        messages = [
            SystemMessage(content=_SYSTEM_PROMPT),
            HumanMessage(
                content=(
                    "## Answer to verify\n\n"
                    f"{answer}\n\n"
                    "## Research notes\n\n"
                    f"{notes_block}"
                )
            ),
        ]
        result: FactCheckResult = self._llm.invoke(messages)
        logger.info(
            "Fact-check complete: overall=%s, support_rate=%.2f",
            result.overall_verdict,
            result.support_rate,
        )
        return result


def build_fact_checker_node():
    """Return a LangGraph-compatible node function that runs the FactCheckerAgent.

    The node reads the last synthesiser message and the accumulated research
    notes, runs the fact-check, and stores the result in the state under the
    ``fact_check_results`` key (added to state as a plain dict so no TypedDict
    change is needed for optional fields).
    """
    agent = FactCheckerAgent()

    def fact_checker(state: ResearchState) -> dict[str, Any]:
        messages = list(state.get("messages", []))
        answer = ""
        for msg in reversed(messages):
            if hasattr(msg, "content") and msg.content:
                answer = str(msg.content)
                break

        research_notes: list[str] = list(state.get("research_notes", []))
        result = agent.check(answer=answer, research_notes=research_notes)

        return {
            "research_notes": [
                *research_notes,
                f"[Fact-check] overall={result.overall_verdict}, "
                f"support_rate={result.support_rate:.0%}, "
                f"unsupported={result.unsupported_count}",
            ],
        }

    return fact_checker
