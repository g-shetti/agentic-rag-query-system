def route(question: str):
    q = question.lower()

    if "trigger" in q:
        return "trigger"

    if "control" in q or "light" in q:
        return "control"

    if "in" in q and ("room" in q or "bedroom" in q or "kitchen" in q):
        return "location"

    return "semantic"
