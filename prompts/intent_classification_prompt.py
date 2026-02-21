def build_intent_classification_prompt(question: str) -> str:
    return f"""
You are a smart home assistant.

Classify the user question into one of the following intents:
1. graph - requires relationship traversal (devices connected, located, triggers, etc.)
2. semantic - requires similarity search (description, vague queries)
3. direct - simple factual question or greeting

Return ONLY one word: graph / semantic / direct

Question: {question}
"""
