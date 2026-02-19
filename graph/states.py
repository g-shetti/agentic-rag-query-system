from typing import TypedDict, List, Annotated
import operator

class GraphState(TypedDict):
    question: str
    cypher: str
    data: list
    answer: str
    retries: int
    error: str

    # IMPORTANT: Annotated with reducer
    reasoning_trace: Annotated[List[str], operator.add]
    retrieved_context: Annotated[List[dict], operator.add]

    confidence_score: float
