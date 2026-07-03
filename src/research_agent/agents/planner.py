def get_sub_queries(plan) -> list:
    """Extract sub-queries from a QueryPlan result safely."""
    if hasattr(plan, "sub_queries"):
        return plan.sub_queries or []
    return []
