"""Unit tests for all 5 research agent nodes."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import tool

from research_agent.state import ResearchState


@tool
def _stub_search_tool(query: str) -> str:
    """Stub search tool used so ToolNode gets a valid tool in tests."""
    return "stub results"


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------


def _base_state(**overrides) -> ResearchState:
    defaults: ResearchState = {
        "messages": [],
        "query": "What is LangGraph?",
        "research_notes": [],
        "document_context": "",
        "citations": [],
        "next": "",
    }
    defaults.update(overrides)
    return defaults


def _ai_msg(content: str) -> AIMessage:
    return AIMessage(content=content)


# ---------------------------------------------------------------------------
# Researcher node
# ---------------------------------------------------------------------------


class TestResearcherNode:
    @patch("research_agent.agents.researcher.ChatAnthropic")
    @patch("research_agent.agents.researcher.get_search_tool")
    def test_returns_messages(self, mock_search, mock_llm_cls):
        mock_llm = MagicMock()
        mock_llm.bind_tools.return_value = mock_llm
        mock_llm.invoke.return_value = _ai_msg("Research result")
        mock_llm_cls.return_value = mock_llm
        mock_search.return_value = _stub_search_tool

        from research_agent.agents.researcher import build_researcher_node

        researcher, _, _ = build_researcher_node()

        state = _base_state(messages=[HumanMessage(content="Tell me about LangGraph")])
        result = researcher(state)

        assert "messages" in result
        assert len(result["messages"]) == 1
        assert result["messages"][0].content == "Research result"

    @patch("research_agent.agents.researcher.ChatAnthropic")
    @patch("research_agent.agents.researcher.get_search_tool")
    def test_routes_to_tools_when_tool_calls_present(self, mock_search, mock_llm_cls):
        mock_llm = MagicMock()
        mock_llm.bind_tools.return_value = mock_llm
        response = _ai_msg("Using tools")
        response.tool_calls = [{"name": "search", "args": {}, "id": "1"}]
        mock_llm.invoke.return_value = response
        mock_llm_cls.return_value = mock_llm
        mock_search.return_value = _stub_search_tool

        from research_agent.agents.researcher import build_researcher_node

        _, _, should_use_tools = build_researcher_node()

        state = _base_state(messages=[response])
        assert should_use_tools(state) == "tools"

    @patch("research_agent.agents.researcher.ChatAnthropic")
    @patch("research_agent.agents.researcher.get_search_tool")
    def test_routes_to_analyst_when_no_tool_calls(self, mock_search, mock_llm_cls):
        mock_llm = MagicMock()
        mock_llm.bind_tools.return_value = mock_llm
        response = _ai_msg("Done researching")
        response.tool_calls = []
        mock_llm.invoke.return_value = response
        mock_llm_cls.return_value = mock_llm
        mock_search.return_value = _stub_search_tool

        from research_agent.agents.researcher import build_researcher_node

        _, _, should_use_tools = build_researcher_node()

        state = _base_state(messages=[response])
        assert should_use_tools(state) == "analyst"


# ---------------------------------------------------------------------------
# Analyst node
# ---------------------------------------------------------------------------


class TestAnalystNode:
    @patch("research_agent.agents.analyst.ChatAnthropic")
    def test_returns_research_notes_and_next(self, mock_llm_cls):

        mock_analysis = MagicMock()
        mock_analysis.summary = "Summary of findings"
        mock_analysis.key_findings = ["Finding 1", "Finding 2"]
        mock_analysis.gaps = ["Gap A"]
        mock_analysis.confidence = "high"
        mock_analysis.source_breakdown = {"web": 3, "documents": 1}

        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value = mock_llm
        mock_llm.invoke.return_value = mock_analysis
        mock_llm_cls.return_value = mock_llm

        from research_agent.agents.analyst import build_analyst_node

        analyst = build_analyst_node()

        state = _base_state(messages=[_ai_msg("Raw research data")])
        result = analyst(state)

        assert "research_notes" in result
        assert "next" in result
        assert result["next"] == "synthesizer"
        assert any("Summary" in note for note in result["research_notes"])
        assert any("Finding" in note for note in result["research_notes"])

    @patch("research_agent.agents.analyst.ChatAnthropic")
    def test_note_structure(self, mock_llm_cls):
        mock_analysis = MagicMock()
        mock_analysis.summary = "Test summary"
        mock_analysis.key_findings = ["F1"]
        mock_analysis.gaps = []
        mock_analysis.confidence = "medium"
        mock_analysis.source_breakdown = {}

        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value = mock_llm
        mock_llm.invoke.return_value = mock_analysis
        mock_llm_cls.return_value = mock_llm

        from research_agent.agents.analyst import build_analyst_node

        analyst = build_analyst_node()

        result = analyst(_base_state())
        notes = result["research_notes"]
        assert isinstance(notes, list)
        assert len(notes) >= 3  # summary + key findings + gaps + confidence


# ---------------------------------------------------------------------------
# Synthesizer node
# ---------------------------------------------------------------------------


class TestSynthesizerNode:
    @patch("research_agent.agents.synthesizer.ChatAnthropic")
    def test_returns_messages_and_end(self, mock_llm_cls):
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = _ai_msg("Final report content")
        mock_llm_cls.return_value = mock_llm

        from research_agent.agents.synthesizer import build_synthesizer_node

        synthesizer = build_synthesizer_node()

        state = _base_state(research_notes=["Note 1", "Note 2"])
        result = synthesizer(state)

        assert "messages" in result
        assert result["messages"][-1].content == "Final report content"
        assert result.get("next") == "end"

    @patch("research_agent.agents.synthesizer.ChatAnthropic")
    def test_passes_notes_to_llm(self, mock_llm_cls):
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = _ai_msg("Answer")
        mock_llm_cls.return_value = mock_llm

        from research_agent.agents.synthesizer import build_synthesizer_node

        synthesizer = build_synthesizer_node()

        notes = ["Note A", "Note B"]
        synthesizer(_base_state(research_notes=notes))

        call_args = mock_llm.invoke.call_args[0][0]
        # The human message should contain the notes
        human_content = " ".join(str(m.content) for m in call_args if hasattr(m, "content"))
        assert "Note A" in human_content


# ---------------------------------------------------------------------------
# Retriever agent node
# ---------------------------------------------------------------------------


class TestRetrieverAgentNode:
    @patch("research_agent.agents.retriever_agent.ChatAnthropic")
    @patch("research_agent.agents.retriever_agent.retrieve")
    @patch("research_agent.agents.retriever_agent.format_context")
    def test_returns_citations_and_notes(self, mock_fmt, mock_retrieve, mock_llm_cls):
        from langchain_core.documents import Document

        mock_doc = Document(
            page_content="LangGraph is a library for building stateful agents.",
            metadata={"filename": "langraph.pdf", "source": "langraph.pdf"},
        )
        mock_retrieve.return_value = [mock_doc]
        mock_fmt.return_value = "[1] Source: langraph.pdf\nLangGraph is..."

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = _ai_msg("Retriever assessment")
        mock_llm_cls.return_value = mock_llm

        from research_agent.agents.retriever_agent import build_retriever_agent_node

        retriever_agent = build_retriever_agent_node()

        result = retriever_agent(_base_state())

        assert "messages" in result
        assert "research_notes" in result
        assert "citations" in result
        assert len(result["citations"]) == 1
        assert result["citations"][0]["source"] == "langraph.pdf"

    @patch("research_agent.agents.retriever_agent.ChatAnthropic")
    @patch("research_agent.agents.retriever_agent.retrieve")
    def test_no_docs_returns_empty_citations(self, mock_retrieve, mock_llm_cls):
        mock_retrieve.return_value = []
        mock_llm_cls.return_value = MagicMock()

        from research_agent.agents.retriever_agent import build_retriever_agent_node

        retriever_agent = build_retriever_agent_node()

        result = retriever_agent(_base_state())
        assert result["citations"] == []
        assert result["research_notes"]  # should still have a note


# ---------------------------------------------------------------------------
# Supervisor node
# ---------------------------------------------------------------------------


class TestSupervisorNode:
    @patch("research_agent.agents.supervisor.ChatAnthropic")
    def test_routes_to_correct_agent(self, mock_llm_cls):
        from research_agent.agents.supervisor import SupervisorDecision

        decision = SupervisorDecision(next="researcher", reasoning="Need more data")
        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value = mock_llm
        mock_llm.invoke.return_value = decision
        mock_llm_cls.return_value = mock_llm

        from research_agent.agents.supervisor import build_supervisor_node

        supervisor, _route = build_supervisor_node()

        result = supervisor(_base_state())
        assert result["next"] == "researcher"

    @patch("research_agent.agents.supervisor.ChatAnthropic")
    def test_finish_maps_to_end(self, mock_llm_cls):
        from research_agent.agents.supervisor import SupervisorDecision

        decision = SupervisorDecision(next="FINISH", reasoning="Report is complete")
        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value = mock_llm
        mock_llm.invoke.return_value = decision
        mock_llm_cls.return_value = mock_llm

        from research_agent.agents.supervisor import build_supervisor_node

        supervisor, _route = build_supervisor_node()

        result = supervisor(_base_state())
        assert result["next"] == "end"

    @patch("research_agent.agents.supervisor.ChatAnthropic")
    def test_route_returns_state_next(self, mock_llm_cls):
        mock_llm_cls.return_value = MagicMock()

        from research_agent.agents.supervisor import build_supervisor_node

        _, route = build_supervisor_node()

        state = _base_state(next="analyst")
        assert route(state) == "analyst"
