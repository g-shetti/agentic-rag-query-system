def should_retry(state):
    error = state.get("error")
    retries = state.get("retries", 0)

    if error and retries < 2:
        return "retry"

    return "end"
