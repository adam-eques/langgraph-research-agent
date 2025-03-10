

class EvalItemRequest(BaseModel):
    query: str
    expected_answer: str = ""
    expected_sources: list[str] = []


class EvalReportResponse(BaseModel):
    total: int
    mean_relevance: float
    mean_faithfulness: float
    mean_context_recall: float
    items: list[dict] = []
