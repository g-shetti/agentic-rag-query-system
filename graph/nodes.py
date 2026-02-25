from prompts.intent_classification_prompt import build_intent_classification_prompt
from prompts.tool_prompt import build_tool_prompt
from services.neo4j_service import Neo4jService
from services.gemini_service import GeminiService
from services.embedding_service import EmbeddingService

neo4j_service = Neo4jService()
gemini_service = GeminiService()

def init_state(state):
    state.setdefault("reasoning_trace", [])
    state.setdefault("retrieved_context", [])
    state.setdefault("retries", 0)
    return state

def reason(state):
    state = init_state(state)

    MAX_RETRIES = 2

    retries = state.get("retries", 0)
    question = state["question"]
    observation = state.get("observation")

    if retries > MAX_RETRIES:
        return {
            **state,
            "intent": "direct",
            "reasoning_trace": [
                "[reason] forced direct (retry overflow)"
            ]
        }

    try:
        if observation == "error":
            intent = "semantic"

        elif observation == "no_data":
            if retries == 1:
                intent = "semantic"
            elif retries >= 2:
                intent = "direct"

        else:
            prompt = build_intent_classification_prompt(question)
            intent = gemini_service.generate_text(prompt)
            intent = intent.lower().strip().replace(".", "").split()[0]

        if intent not in ["graph", "semantic", "direct"]:
            intent = "graph"

        return {
            **state,
            "intent": intent,
            "reasoning_trace": [
                f"[reason] intent={intent}, retries={retries}, observation={observation}"
            ]
        }

    except Exception as e:
        return {
            **state,
            "intent": "graph",
            "error": str(e),
            "reasoning_trace": [
                f"[reason] failed, fallback=graph: {str(e)}"
            ]
        }

def tool_router(state):
    state = init_state(state)
    question = state["question"]

    try:
        decision = gemini_service.generate_structured(
            build_tool_prompt(question)
        )

        tool = decision.get("tool", "execute_cypher_query")

        return {
            **state,
            "selected_tool": tool,
            "tool_input": decision.get("input", {}),
            "reasoning_trace": [
                f"[router] selected_tool={tool}"
            ]
        }

    except Exception as e:
        return {
            **state,
            "selected_tool": "execute_cypher_query",
            "reasoning_trace": [
                f"[router] fallback graph: {str(e)}"
            ]
        }
    
def verify(state: dict) -> dict:
    state = init_state(state)

    data = state.get("data", [])
    error = state.get("error")
    retries = state.get("retries", 0)
    intent = state.get("intent")

    MAX_RETRIES = 2

    if intent == "direct":
        return {
            **state,
            "is_sufficient": True,
            "observation": "direct",
            "reasoning_trace": [
                "[verify] direct intent → sufficient"
            ]
        }

    if error:
        if retries >= MAX_RETRIES:
            return {
                **state,
                "is_sufficient": True,
                "observation": "error_final",
                "reasoning_trace": [
                    "[verify] error but max retries reached → answer"
                ]
            }

        return {
            **state,
            "is_sufficient": False,
            "observation": "error",
            "retries": retries + 1,
            "reasoning_trace": [
                "[verify] error → retry"
            ]
        }

    if isinstance(data, list) and len(data) > 0:
        return {
            **state,
            "is_sufficient": True,
            "observation": "data_found",
            "reasoning_trace": [
                f"[verify] data found ({len(data)}) → sufficient"
            ]
        }

    if retries >= MAX_RETRIES:
        return {
            **state,
            "is_sufficient": True,
            "observation": "no_data_final",
            "reasoning_trace": [
                "[verify] no data but max retries → answer"
            ]
        }

    return {
        **state,
        "is_sufficient": False,
        "observation": "no_data",
        "retries": retries + 1,
        "reasoning_trace": [
            "[verify] no data → retry"
        ]
    }

def semantic_search(state):
    state = init_state(state)

    question = state["question"]

    try:
        embedding = EmbeddingService().embed(question)
        results = neo4j_service.vector_search(embedding)

        return {
            **state,
            "data": results,
            "error": None,
            "retrieved_context": [{
                "source": "vector",
                "query": question,
                "results": results
            }],
            "reasoning_trace": [
                f"[semantic] retrieved={len(results)}"
            ]
        }

    except Exception as e:
        return {
            **state,
            "data": [],
            "error": str(e),
            "reasoning_trace": [
                f"[semantic] failed: {str(e)}"
            ]
        }

def validate_cypher(query):
    forbidden = ["CREATE", "DELETE", "MERGE", "SET"]
    for word in forbidden:
        if word in query.upper():
            raise Exception("Unsafe query generated")
    return query

def generate_cypher(state):
    state = init_state(state)

    question = state["question"]

    try:
        cypher = gemini_service.generate_cypher(question)
        cypher = validate_cypher(cypher)

        return {
            **state,
            "cypher": cypher,
            "data": [],
            "error": None,
            "reasoning_trace": [
                "[generate] cypher created"
            ]
        }

    except Exception as e:
        return {
            **state,
            "data": [],
            "error": str(e),
            "reasoning_trace": [
                f"[generate] failed: {str(e)}"
            ]
        }
    
def run_query(state):
    state = init_state(state)

    cypher = state.get("cypher")

    if not cypher:
        return {
            **state,
            "data": [],
            "error": "No Cypher query",
            "reasoning_trace": [
                "[execute] missing cypher"
            ]
        }

    try:
        data = neo4j_service.run_query(cypher)

        return {
            **state,
            "data": data,
            "error": None,
            "retrieved_context": [{
                "source": "graph",
                "cypher": cypher,
                "results": data
            }],
            "reasoning_trace": [
                f"[execute] retrieved={len(data)}"
            ]
        }

    except Exception as e:
        return {
            **state,
            "error": str(e),
            "data": [],
            "reasoning_trace": [
                f"[execute] failed: {str(e)}"
            ]
        }
    
def generate_answer(state):
    state = init_state(state)

    question = state["question"]
    data = state.get("data", [])
    error = state.get("error")
    intent = state.get("intent", "graph")

    if intent == "direct":
        try:
            answer = gemini_service.generate_text(
                f"Respond politely:\n{question}"
            )

            return {
                **state,
                "answer": answer,
                "reasoning_trace": [
                    "[answer] direct response"
                ]
            }

        except Exception:
            return {
                **state,
                "answer": "Hello! How can I assist you?",
                "reasoning_trace": [
                    "[answer] fallback direct"
                ]
            }

    if error:
        return {
            **state,
            "answer": f"Error: {error}",
            "reasoning_trace": [
                "[answer] error fallback"
            ]
        }

    try:

        if not data:
            return {
                **state,
                "answer": "No matching devices found",
                "reasoning_trace": [
                    "[answer] no data fallback"
                ]
            }

        answer = gemini_service.generate_answer(
            question=question,
            data=str(data)
        )

        return {
            **state,
            "answer": answer,
            "reasoning_trace": [
                "[answer] generated"
            ]
        }

    except Exception as e:
        return {
            **state,
            "error": str(e),
            "answer": "Failed to generate answer",
            "reasoning_trace": [
                f"[answer] failed: {str(e)}"
            ]
        }
    
def compute_confidence(state):
    state = init_state(state)

    data = state.get("data", [])
    error = state.get("error")

    if error:
        confidence = 0.0
    elif not data:
        confidence = 0.3
    else:
        confidence = min(1.0, 0.5 + 0.1 * len(data))

    return {
        **state,
        "confidence_score": round(confidence, 2),
        "reasoning_trace": [
            f"[confidence] {round(confidence, 2)}"
        ]
    }