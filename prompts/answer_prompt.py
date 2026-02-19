def build_answer_prompt(question: str, data: list) -> str:
    return f"""
You are a smart home assistant.

User question:
{question}

Database result:
{data}

Instructions:
- Answer clearly in plain English
- Do NOT mention database or cypher
- If no data, say "No matching devices found"
- If data exists, list devices properly

Answer:
"""
