def build_answer_prompt(question: str, data: list) -> str:
    return f"""
You are a smart home assistant.

Answer the question using ONLY the provided data.

Guidelines:
- Be concise and clear
- Present results as a natural sentence or bullet points if multiple items
- Do NOT mention database, cypher, or internal processing
- If no data is available, respond exactly: "No matching devices found"
- Do NOT hallucinate or assume missing data

Question:
{question}

Data:
{data}

Answer:
"""