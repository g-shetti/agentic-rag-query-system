from fastapi import FastAPI
from pydantic import BaseModel
from services.neo4j_service import Neo4jService
from services.gemini_service import GeminiService
from fastapi.middleware.cors import CORSMiddleware
from graph.workflow import build_graph

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

neo4j = Neo4jService()
gemini = GeminiService()
graph = build_graph()

class QueryRequest(BaseModel):
    question: str

# @app.post("/query")
# def query(request: QueryRequest):
#     try:
#         print("Received question:", request.question)

#         # Step 1: Generate Cypher
#         cypher_query = gemini.generate_cypher(request.question)
#         cypher_query = validate_cypher(cypher_query)

#         print("Generated Cypher:", cypher_query)

#         # Step 2: Run query
#         data = neo4j.run_query(cypher_query)
#         print("Data:", data)

#         # Step 3: Generate answer
#         answer = gemini.generate_answer(
#             question=request.question,
#             data=str(data)
#         )
#         print("Generated Answer:", answer)

#         return {
#             "question": request.question,
#             "cypher_query": cypher_query,
#             "data": data,
#             "answer": answer
#         }

#     except Exception as e:
#         return {"error": str(e)}

@app.post("/query")
def query(request: QueryRequest):

    print("Received question:", request.question)

    result = graph.invoke({
        "question": request.question
    })

    print("Generated Cypher:", result.get("cypher"))
    print("Data:", result.get("data"))
    print("Generated Answer:", result.get("answer"))

    return {
        "question": request.question,
        "cypher_query": result.get("cypher"),
        "data": result.get("data"),
        "answer": result.get("answer")
    }

def validate_cypher(query):
    forbidden = ["CREATE", "DELETE", "MERGE", "SET"]
    for word in forbidden:
        if word in query.upper():
            raise Exception("Unsafe query generated")
    return query
