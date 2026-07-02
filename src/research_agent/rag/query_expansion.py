"""Query expansion via LLM — generates alternative phrasings for better retrieval coverage."""

from __future__ import annotations

import logging

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from research_agent.config import config

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """You are a search query optimisation expert. Given a user's original \
research question, generate alternative phrasings and related queries that will improve \
document retrieval coverage.

Guidelines:
- Rephrase the query using different vocabulary (synonyms, technical vs. lay terms)
- Add queries that address different aspects of the same topic
- Consider both broad and narrow formulations
- Keep each alternative concise and focused
- Do NOT change the fundamental intent of the original query
- The alternatives should complement, not duplicate, each other
"""


class ExpandedQueries(BaseModel):
    """Structured output for query expansion."""

    alternatives: list[str] = Field(
        description="Alternative phrasings of the original query",
        min_length=1,
        max_length=10,
    )
    reasoning: str = Field(description="Brief explanation of the expansion strategy used")


class QueryExpander:
    """Generates N alternative phrasings of a query for better retrieval coverage.

    Uses a single ChatAnthropic call with structured output to produce
    semantically-varied alternatives.  The original query is always prepended
    to the returned list so callers receive ``[original] + alternatives``.

    Example
    -------
    >>> expander = QueryExpander()
    >>> queries = expander.expand("How does transformer attention work?", n=3)
    >>> len(queries)
    4  # original + 3 alternatives
    """

    def __init__(self) -> None:
        self._llm = ChatAnthropic(
            model=config.default_model,
            temperature=0.3,  # small temperature for creative variation
            max_tokens=1024,
            api_key=config.anthropic_api_key,
        ).with_structured_output(ExpandedQueries)

    def expand(self, query: str, n: int = 3) -> list[str]:
        """Generate *n* alternative phrasings and prepend the original query.

        Parameters
        ----------
        query:
            The original search query to expand.
        n:
            Number of alternative phrasings to generate (1-10).

        Returns
        -------
        list[str]
            ``[original_query, alt_1, alt_2, ..., alt_n]``.  The list always
            starts with the original query.  If the LLM returns fewer
            alternatives than requested they are all included.
        """
        n = max(1, min(n, 10))
        logger.debug("Expanding query (n=%d): %.100s", n, query)

        messages = [
            SystemMessage(content=_SYSTEM_PROMPT),
            HumanMessage(
                content=(f"Original query: {query}\n\nGenerate exactly {n} alternative phrasings.")
            ),
        ]

        try:
            result: ExpandedQueries = self._llm.invoke(messages)
            alternatives = result.alternatives[:n]
        except Exception:
            logger.exception("Query expansion failed — returning original query only")
            return [query]

        # Deduplicate while preserving order, always keeping original first.
        seen: set[str] = {query.lower()}
        deduped: list[str] = [query]
        for alt in alternatives:
            if alt.lower() not in seen:
                seen.add(alt.lower())
                deduped.append(alt)

        logger.debug(
            "Expanded to %d queries (requested %d): %s",
            len(deduped),
            n + 1,
            deduped,
        )
        return deduped
