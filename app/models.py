from pydantic import BaseModel
from typing import List, Optional, Any


class QueryRequest(BaseModel):
    question: str
    include_reasoning: Optional[bool] = False


class QueryResponse(BaseModel):
    answer: str
    reasoning_trace: Optional[List[str]] = None
    retrieved_context: Optional[List[str]] = None
    confidence_score: float
