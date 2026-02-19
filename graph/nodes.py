from services.neo4j_service import Neo4jService
from services.gemini_service import GeminiService

neo4j_service = Neo4jService()
gemini_service = GeminiService()

def init_state(state):
    """Ensure all required keys exist"""
    state.setdefault("reasoning_trace", [])
    state.setdefault("retrieved_context", [])
    state.setdefault("retries", 0)
    return state

def validate_cypher(query):
    forbidden = ["CREATE", "DELETE", "MERGE", "SET"]
    for word in forbidden:
        if word in query.upper():
            raise Exception("Unsafe query generated")
    return query

def generate_cypher(state):
    state = init_state(state)

    question = state["question"]
    retries = state["retries"]

    print("Generating Cypher for question:", question)
    print(f"Retries so far: {retries}")

    try:
        cypher = gemini_service.generate_cypher(question)

        # Safety validation
        cypher = validate_cypher(cypher)

        state["cypher"] = cypher
        state["retries"] = retries + 1

        state["reasoning_trace"].append(
            f"[generate] Generated Cypher query: {cypher}"
        )

    except Exception as e:
        state["error"] = str(e)
        state["reasoning_trace"].append(
            f"[generate] Failed to generate Cypher: {str(e)}"
        )

    return state

def run_query(state):
    state = init_state(state)

    cypher = state.get("cypher")

    print("Running Cypher query:", cypher)

    if not cypher:
        state["error"] = "No Cypher query found"
        state["reasoning_trace"].append(
            "[execute] No Cypher query to execute"
        )
        return state

    try:
        data = neo4j_service.run_query(cypher)

        state["data"] = data

        # Add retrieved context
        state["retrieved_context"].append({
            "source": "graph",
            "cypher": cypher,
            "results": data
        })

        state["reasoning_trace"].append(
            f"[execute] Query executed successfully, retrieved {len(data)} records"
        )

    except Exception as e:
        state["error"] = str(e)
        state["reasoning_trace"].append(
            f"[execute] Query failed: {str(e)}"
        )

    return state

def generate_answer(state):
    state = init_state(state)

    question = state["question"]
    data = state.get("data", [])
    error = state.get("error")

    print("Generating answer for question:", question)

    if error:
        state["answer"] = f"Error occurred: {error}"
        state["reasoning_trace"].append(
            "[answer] Skipped answer generation due to error"
        )
        return state

    try:
        answer = gemini_service.generate_answer(
            question=question,
            data=str(data)
        )

        state["answer"] = answer

        state["reasoning_trace"].append(
            "[answer] Generated final answer from retrieved data"
        )

    except Exception as e:
        state["error"] = str(e)
        state["answer"] = "Failed to generate answer"
        state["reasoning_trace"].append(
            f"[answer] Failed to generate answer: {str(e)}"
        )

    return state

def compute_confidence(state):
    state = init_state(state)

    data = state.get("data", [])
    error = state.get("error")

    if error:
        confidence = 0.0

    elif not data:
        confidence = 0.3

    else:
        # simple heuristic
        confidence = min(1.0, 0.5 + 0.1 * len(data))

    state["confidence_score"] = round(confidence, 2)

    state["reasoning_trace"].append(
        f"[confidence] Computed confidence score: {state['confidence_score']}"
    )

    return state
