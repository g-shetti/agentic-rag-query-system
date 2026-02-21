def build_tool_prompt(question):
    return f"""
You are a smart home assistant.

Available tools:
1. execute_cypher_query(query)
2. semantic_search(query, top_k)
3. get_device_state(device_id)

Return JSON:
{{
  "tool": "execute_cypher_query | semantic_search | get_device_state | none",
  "input": {{
    "query": "...",
    "device_id": "...",
    "top_k": 5
  }}
}}

Question:
{question}
"""