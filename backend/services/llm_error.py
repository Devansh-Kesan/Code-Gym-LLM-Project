from .query_llm import chat_with_llm

def generate_error_explanation(question_title: str, question_description: str, user_code: str) -> str:
    prompt = f"""
You are a helpful assistant that analyzes Python code and explains errors.

Problem: {question_title}
Description: {question_description}

Student Code:
{user_code}

Explain any runtime or compile-time errors in plain English. DO NOT fix the code, only explain the issue and suggest a general direction to fix it.
"""
    response = chat_with_llm(prompt)
    return response