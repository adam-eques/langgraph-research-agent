"""Query planner agent — decomposes complex queries into sub-queries before retrieval."""
from __future__ import annotations

import logging
from typing import Literal

from pydantic import BaseModel, Field
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage

from research_agent.config import config
from research_agent.state import ResearchState

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """You are a research planning expert. Your job is to analyze a user's complex \
research question and break it down into a set of focused, atomic sub-queries that together \
will fully answer the original question.

Guidelines:
- Decompose broad, multi-faceted questions into 2–5 specific sub-queries
- Each sub-query should be independently answerable
- Order sub-queries logically (foundational context before advanced detail)
- Avoid redundancy between sub-queries
- Assess the overall complexity so downstream agents can calibrate their effort
- Choose the right retrieval strategy: 'web_first' for current events, 'docs_first' for \
  domain-specific archives, 'hybrid' for questions needing both
"""


class QueryPlan(BaseModel):
    """Structured decomposition of a complex research question."""

    sub_queries: list[str] = Field(
        description="Ordered list of 2–5 focused sub-queries derived from the original question",
        min_length=1,
        max_length=5,
    )
    strategy: Literal["web_first", "docs_first", "hybrid"] = Field(
        description=(
            "Retrieval strategy: 'web_first' for live/current info, "
            "'docs_first' for document-grounded answers, "
            "'hybrid' for both"
        )
    )
    estimated_complexity: Literal["low", "medium", "high"] = Field(
        description=(
            "Estimated effort to answer the query: "
            "low = simple factual, medium = multi-step, high = synthesis across many sources"
        )
    )
    rationale: str = Field(
        description="Brief explanation of why the query was decomposed this way"
    )


class QueryPlannerAgent:
    """Decomposes a complex research query into focused sub-queries.

    This agent is an optional first step in the research pipeline.  It is most
    valuable when the user's question is broad, multi-faceted, or requires
    combining information from different domains.

    Example
    -------
    >>> planner = QueryPlannerAgent()
    >>> plan = planner.plan("Compare the economic impacts of AI adoption in healthcare and finance")
    >>> plan.sub_queries
    ['What is the economic impact of AI in healthcare?', ...]
    """

    def __init__(self) -> None:
        self._llm = ChatAnthropic(
            model=config.default_model,
            temperature=0,
            max_tokens=1024,
            api_key=config.anthropic_api_key,
        ).with_structured_output(QueryPlan)

    def plan(self, query: str) -> QueryPlan:
        """Break a complex query into sub-queries and return a QueryPlan.

        Parameters
        ----------
        query:
            The original user query to decompose.

        Returns
        -------
        QueryPlan
            Structured plan with sub-queries, strategy, and complexity estimate.
        """
        logger.info("Planning query decomposition for: %.120s", query)
        messages = [
            SystemMessage(content=_SYSTEM_PROMPT),
            HumanMessage(content=f"Research question to decompose:\n\n{query}"),
        ]
        plan: QueryPlan = self._llm.invoke(messages)
        logger.info(
            "Query plan: %d sub-queries, strategy=%s, complexity=%s",
            len(plan.sub_queries),
            plan.strategy,
            plan.estimated_complexity,
        )
        return plan


def build_planner_node():
    """Return a LangGraph-compatible node function that runs the QueryPlannerAgent.

    The node injects the plan into ``research_notes`` and sets the query list
    onto the state so downstream retriever/researcher nodes can iterate over
    sub-queries.
    """
    agent = QueryPlannerAgent()

    def planner(state: ResearchState) -> ResearchState:
        query = state["query"]
        plan = agent.plan(query)

        # Materialise the plan as research notes so analysts can see the structure.
        plan_notes = [
            f"Query plan ({plan.estimated_complexity} complexity, strategy={plan.strategy}):",
            f"Rationale: {plan.rationale}",
            "Sub-queries:",
            *[f"  {i+1}. {sq}" for i, sq in enumerate(plan.sub_queries)],
        ]

        return {
            "research_notes": plan_notes,
            "next": "retriever",
        }

    return planner
