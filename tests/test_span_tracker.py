from __future__ import annotations
import time
from research_agent.span_tracker import SpanTracker, Span


def test_start_and_end_span():
    st = SpanTracker()
    span = st.start_span("retrieval")
    time.sleep(0.01)
    st.end_span(span)
    assert span.duration_ms >= 10 and span.status == "ok"


def test_context_manager():
    st = SpanTracker()
    with st.span("analyse") as s:
        time.sleep(0.001)
    assert s.end_time is not None


def test_to_dict():
    st = SpanTracker()
    with st.span("step1"):
        pass
    d = st.to_dict()
    assert len(d) == 1 and "name" in d[0]


def test_error_status_on_exception():
    st = SpanTracker()
    try:
        with st.span("fail"):
            raise ValueError("boom")
    except ValueError:
        pass
    assert st.get_spans()[0].status == "error"
