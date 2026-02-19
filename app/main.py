from fastapi import FastAPI
from app.models import QueryRequest, QueryResponse
from graph.workflow import build_graph

app = FastAPI()

graph = build_graph()

print(graph.get_graph().draw_mermaid())

def format_retrieved_context(context_list):
    formatted = []

    for ctx in context_list:
        if ctx.get("source") == "graph":
            results = ctx.get("results", [])

            for record in results:
                # customize based on your schema
                if isinstance(record, dict):
                    text = ", ".join(f"{k}: {v}" for k, v in record.items())
                    formatted.append(text)
                else:
                    formatted.append(str(record))

        elif ctx.get("source") == "vector":
            docs = ctx.get("documents", [])
            formatted.extend(docs)

    return formatted

@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):

    print("Received question:", request.question)

    # ---- Invoke LangGraph ----
    result = graph.invoke({
        "question": request.question,
        "reasoning_trace": [],
        "retrieved_context": []
    })

    print("Generated Cypher:", result.get("cypher"))
    print("Data:", result.get("data"))
    print("Answer:", result.get("answer"))

    # ---- Extract fields ----
    answer = result.get("answer", "No answer generated")
    confidence_score = result.get("confidence_score", 0.0)

    # ---- Format context ----
    retrieved_context = format_retrieved_context(
        result.get("retrieved_context", [])
    )

    # ---- Conditional reasoning ----
    if request.include_reasoning:
        reasoning_trace = result.get("reasoning_trace", [])
    else:
        reasoning_trace = None

    # ---- Response ----
    response = {
        "answer": answer,
        "confidence_score": confidence_score
    }

    if request.include_reasoning:
        response["reasoning_trace"] = reasoning_trace
        response["retrieved_context"] = retrieved_context

    return response
    