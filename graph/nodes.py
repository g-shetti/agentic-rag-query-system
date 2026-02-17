from services.neo4j_service import Neo4jService
from services.gemini_service import GeminiService

neo4j_service = Neo4jService()
gemini_service = GeminiService()

def generate_cypher(state):
    print("Generating Cypher for question:", state["question"])
    retries = state.get("retries", 0)
    print(f"Retries so far: {retries}")
    question = state["question"]

    cypher = gemini_service.generate_cypher(question)

    return {
        **state,
        "cypher": cypher,
        "retries": retries + 1
    }


def run_query(state):
    print("Running Cypher query:", state["cypher"])
    cypher = state["cypher"]

    data = neo4j_service.run_query(cypher)

    return {
        **state,
        "data": data
    }


def generate_answer(state):
    print("Generating answer for question:", state["question"])
    answer = gemini_service.generate_answer(
        question=state["question"],
        data=str(state["data"])
    )

    return {
        **state,
        "answer": answer
    }
