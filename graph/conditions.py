def should_retry(state):
    print("Checking if we should retry...")
    if not state.get("data") and state.get("retries", 0) < 2:
        state["retries"] += 1
        print("Retrying...")
        return "retry"
    return "end"
