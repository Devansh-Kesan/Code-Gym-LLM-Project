from .query_llm import chat_with_llm

def generate_code_review(question_title: str, question_description: str, user_code: str) -> str:
    prompt = f"""
You are a code reviewer. Review the following Python code for style, readability, and performance.

Problem: {question_title}
Description: {question_description}

Student Code:
{user_code}

Provide a constructive review. Suggest optimizations if possible, but DO NOT rewrite the entire code.
"""
    response = chat_with_llm(prompt)
    return response