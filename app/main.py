from fastapi import FastAPI
from pydantic import BaseModel

from app.router import route
from app.retrieval import (
    get_devices_by_location,
    get_triggered_devices,
    get_controllers_of_lights,
    vector_search,
    hybrid_search
)

app = FastAPI()

class QueryRequest(BaseModel):
    question: str

@app.post("/query")
def query(request: QueryRequest):
    intent = route(request.question)

    if intent == "trigger":
        data = get_triggered_devices()

    elif intent == "control":
        data = get_controllers_of_lights()

    elif intent == "location":
        # naive extraction
        if "bedroom" in request.question.lower():
            data = get_devices_by_location("Bedroom")
        elif "kitchen" in request.question.lower():
            data = get_devices_by_location("Kitchen")
        else:
            data = []

    elif intent == "semantic":
        data = vector_search(request.question)

    else:
        data = hybrid_search(request.question)

    return {
        "question": request.question,
        "intent": intent,
        "data": data
    }
