from __future__ import annotations

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from research_agent.config import config
from research_agent.state import ResearchState, Citation
from research_agent.rag.retriever import retrieve, format_context

_SYSTEM_PROMPT = """You are a document retrieval specialist with access to an indexed knowledge base.

Your role:
1. Retrieve the most relevant passages from the document store for the research query
2. Assess how well the retrieved context answers the query
3. Identify what the documents do and do NOT cover
4. Extract specific citations with source attribution
5. Pass the grounded context to the analyst

Always cite document sources precisely. Never fabricate information not found in the retrieved passages.
"""


def build_retriever_agent_node():
    llm = ChatAnthropic(
        model=config.default_model,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        api_key=config.anthropic_api_key,
    )

    def retriever_agent(state: ResearchState) -> ResearchState:
        query = state["query"]
        docs = retrieve(query)

        if not docs:
            return {
                "messages": [AIMessage(content="No relevant documents found in the knowledge base.")],
                "research_notes": ["No document context available — relying on web search only."],
                "citations": [],
            }

        context = format_context(docs)
        citations: list[Citation] = [
            {
                "source": doc.metadata.get("filename", doc.metadata.get("source", "unknown")),
                "excerpt": doc.page_content[:200],
                "relevance": "retrieved by semantic similarity",
            }
            for doc in docs
        ]

        messages = [
            SystemMessage(content=_SYSTEM_PROMPT),
            HumanMessage(content=f"Query: {query}\n\nRetrieved context:\n\n{context}"),
        ]
        response: AIMessage = llm.invoke(messages)
        return {
            "messages": [response],
            "research_notes": [f"Document context retrieved ({len(docs)} passages):\n{context[:500]}..."],
            "citations": citations,
        }

    return retriever_agent
