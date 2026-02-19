from langgraph.graph import StateGraph
from graph.nodes import (
    generate_cypher,
    run_query,
    generate_answer,
    compute_confidence
)
from graph.conditions import should_retry
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

def build_graph():
    print("Building workflow graph...")

    builder = StateGraph(GraphState)

    # ---- Nodes ----
    builder.add_node("generate", generate_cypher)
    builder.add_node("execute", run_query)
    builder.add_node("answer", generate_answer)
    builder.add_node("confidence", compute_confidence)

    # ---- Entry ----
    builder.set_entry_point("generate")

    # ---- Flow ----
    builder.add_edge("generate", "execute")

    # Retry loop
    builder.add_conditional_edges(
        "execute",
        should_retry,
        {
            "retry": "generate",   # regenerate cypher
            "end": "answer"        # proceed
        }
    )

    # Final stages
    builder.add_edge("answer", "confidence")
    builder.add_edge("confidence", "__end__")

    return builder.compile()
