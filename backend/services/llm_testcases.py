from .query_llm import chat_with_llm

def generate_test_cases(question_title: str, question_description: str, user_code: str) -> str:
    prompt = f"""
You are a Python teaching assistant.

Problem: {question_title}
Description: {question_description}

Student Code:
{user_code}

Generate 2-3 additional test cases that might reveal bugs or performance issues. Focus on edge cases and large inputs. Provide inputs and expected outputs.
"""
    response = chat_with_llm(prompt)
    return response
