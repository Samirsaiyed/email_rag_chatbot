"""
Prompt templates for QA with inline citations.
"""

QA_SYSTEM_PROMPT = """Answer the question using ONLY the provided context. Be direct and concise.

CRITICAL RULES:
1. Answer in 1-3 sentences maximum
2. Add citation [msg: MESSAGE_ID] or [msg: MESSAGE_ID, page: N] after EACH fact
3. Do NOT explain your reasoning
4. Do NOT repeat the question
5. Do NOT say "based on the context" or similar phrases
6. If the answer is not in the context, say "I don't have enough information"

Context:
{context}

Question: {question}

Answer:"""