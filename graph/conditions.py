def route_by_intent(state):
    return state.get("intent", "graph")


def should_continue(state: dict) -> str:
    if not state.get("is_sufficient", False):
        return "retry"
    return "answer"

def route_by_tool(state):
    return state.get("selected_tool", "execute_cypher_query")