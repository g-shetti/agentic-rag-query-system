from langgraph.graph import StateGraph
from graph.nodes import generate_cypher, run_query, generate_answer
from graph.conditions import should_retry


def build_graph():
    print("Building workflow graph...")
    builder = StateGraph(dict)

    builder.add_node("generate", generate_cypher)
    builder.add_node("execute", run_query)
    builder.add_node("answer", generate_answer)

    builder.set_entry_point("generate")

    builder.add_edge("generate", "execute")

    builder.add_conditional_edges(
        "execute",
        should_retry,
        {
            "retry": "generate",
            "end": "answer"
        }
    )

    builder.add_edge("answer", "__end__")

    return builder.compile()
