# Agents

## Researcher

Web search agent using the Tavily API. Runs a tool-call loop until the LLM decides it has enough information, then passes control to the analyst.

```python
from research_agent.agents.researcher import build_researcher_node
researcher, tool_node, route_fn = build_researcher_node()
```

Key behavior: loops back through `research_tools` until no more tool calls are made.

## Retriever

Semantic search agent over the indexed document knowledge base. Populates `citations` with source excerpts.

```python
from research_agent.agents.retriever_agent import build_retriever_agent_node
retriever = build_retriever_agent_node()
```

Falls back gracefully when no documents are indexed.

## Analyst

Structured analysis of all gathered context. Returns a `AnalysisOutput` Pydantic model with `key_findings`, `gaps`, `confidence`, and `source_breakdown`.

```python
from research_agent.agents.analyst import build_analyst_node
analyst = build_analyst_node()
```

## Synthesizer

Produces the final, user-facing report. This is the only node that streams tokens to the caller.

## Supervisor

Routes dynamically between all agents. Use when the query requires non-linear orchestration.

```python
graph = build_graph(use_supervisor=True)
```

## Planner

Decomposes complex queries into sub-queries before retrieval and research.

```python
from research_agent.agents.planner import build_planner_node
planner = build_planner_node()
```

Returns `QueryPlan` with `sub_queries`, `strategy`, and `estimated_complexity`.

## Fact Checker

Verifies individual claims in the synthesizer output against the gathered research.

## Citation Verifier

Audits whether citations in the final report are faithfully represented.

## Web Scraper

Extracts full page content from URLs mentioned in researcher messages — provides deeper context than search snippets alone.

## Adding a custom agent

```python
from research_agent.state import ResearchState

def my_agent(state: ResearchState) -> ResearchState:
    # Read from state
    query = state["query"]
    messages = state["messages"]
    # Return partial state update
    return {"research_notes": ["Custom agent result"]}

# Add to graph
graph.add_node("my_agent", my_agent)
graph.add_edge("analyst", "my_agent")
graph.add_edge("my_agent", "synthesizer")
```
