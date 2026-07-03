from __future__ import annotations

import logging
from typing import cast

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from research_agent.config import config
from research_agent.state import ResearchState

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """You are a citation verifier. Given a research answer and its citations, \
verify that each citation actually supports the claim it is used to back.

For each citation:
- Read the excerpt
- Check if the answer uses it faithfully
- Flag any citation that is misrepresented, overstated, or unrelated
- Assign a verification status: VERIFIED, WEAK, or INVALID
"""


class CitationVerification(BaseModel):
    source: str
    status: str = Field(description="VERIFIED, WEAK, or INVALID")
    note: str = Field(description="Brief explanation of the verification result")


class VerificationResult(BaseModel):
    verifications: list[CitationVerification]
    all_valid: bool
    issues: list[str] = Field(default_factory=list)


def build_citation_verifier_node():
    llm = ChatAnthropic(
        model=config.default_model,
        temperature=0,
        max_tokens=2048,
        api_key=config.anthropic_api_key,
    ).with_structured_output(VerificationResult)

    def citation_verifier(state: ResearchState) -> ResearchState:
        citations = state.get("citations", [])
        if not citations:
            logger.debug("No citations to verify")
            return {}

        messages = state.get("messages", [])
        answer = messages[-1].content if messages else ""

        citations_text = "\n".join(
            f"[{i + 1}] {c['source']}: {c['excerpt'][:300]}" for i, c in enumerate(citations)
        )

        result = cast(
            VerificationResult,
            llm.invoke(
                [
                    SystemMessage(content=_SYSTEM_PROMPT),
                    HumanMessage(
                        content=(
                            f"Answer:\n{answer}\n\n"
                            f"Citations:\n{citations_text}\n\n"
                            "Verify each citation."
                        )
                    ),
                ]
            ),
        )

        logger.info(
            "Citation verification: %d/%d valid",
            sum(1 for v in result.verifications if v.status == "VERIFIED"),
            len(result.verifications),
        )

        if not result.all_valid:
            invalid = [v.source for v in result.verifications if v.status == "INVALID"]
            logger.warning("Invalid citations detected: %s", invalid)

        return {
            "research_notes": [
                *state.get("research_notes", []),
                f"Citation check: {'PASS' if result.all_valid else 'ISSUES FOUND'} "
                f"— {len(result.verifications)} citations reviewed",
            ]
        }

    return citation_verifier
