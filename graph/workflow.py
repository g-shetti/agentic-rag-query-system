from langgraph.graph import StateGraph, END
from graph.nodes import (
    generate_cypher,
    reason,
    run_query,
    generate_answer,
    compute_confidence,
    semantic_search,
    tool_router,
    verify
)
from graph.conditions import route_by_tool, should_continue
from graph.states import GraphState

def build_graph():
    builder = StateGraph(GraphState)

    builder.add_node("reason", reason)
    builder.add_node("router", tool_router)
    builder.add_node("generate", generate_cypher)
    builder.add_node("execute", run_query)
    builder.add_node("semantic", semantic_search)
    builder.add_node("verify", verify)
    builder.add_node("answer", generate_answer)
    builder.add_node("confidence", compute_confidence)

    builder.set_entry_point("reason")

    builder.add_edge("reason", "router")

    builder.add_conditional_edges(
        "router",
        route_by_tool,
        {
            "execute_cypher_query": "generate",
            "semantic_search": "semantic",
            "get_device_state": "execute",
            "none": "verify"
        }
)

    builder.add_edge("generate", "execute")
    builder.add_edge("execute", "verify")

    builder.add_edge("semantic", "verify")

    builder.add_conditional_edges(
        "verify",
        should_continue,
        {
            "retry": "reason",
            "answer": "answer",
        }
    )

    builder.add_edge("answer", "confidence")
    builder.add_edge("confidence", END)

    return builder.compile()

graph = build_graph()