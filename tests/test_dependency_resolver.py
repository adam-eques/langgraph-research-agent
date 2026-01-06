from __future__ import annotations

import pytest
from research_agent.dependency_resolver import DependencyResolver


def test_simple_linear_order():
    r = DependencyResolver()
    r.register("a")
    r.register("b", depends_on=["a"])
    r.register("c", depends_on=["b"])
    order = r.resolve()
    assert order.index("a") < order.index("b")
    assert order.index("b") < order.index("c")


def test_no_dependencies():
    r = DependencyResolver()
    r.register("x")
    r.register("y")
    order = r.resolve()
    assert set(order) == {"x", "y"}


def test_circular_dependency_raises():
    r = DependencyResolver()
    r.register("a", depends_on=["b"])
    r.register("b", depends_on=["a"])
    with pytest.raises(ValueError, match="Circular"):
        r.resolve()
