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
            for record in ctx.get("results", []):
                formatted.append(str(record))

        elif ctx.get("source") == "vector":
            for record in ctx.get("results", []):
                formatted.append(
                    f"{record.get('device_id')} - {record.get('description')}"
                )

    return formatted

@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    try:
        result = graph.invoke({
            "question": request.question,
            "reasoning_trace": [],
            "retrieved_context": []
        })

        formatted_context = format_retrieved_context(
            result.get("retrieved_context", [])
        )

        response = {
            "answer": result.get("answer"),
            "confidence_score": result.get("confidence_score", 0),
            "retrieved_context": formatted_context
        }

        if request.include_reasoning:
            response["reasoning_trace"] = result.get("reasoning_trace", [])

        return response

    except Exception as e:
        return {
            "answer": "System error occurred",
            "error": str(e),
            "confidence_score": 0
        }
