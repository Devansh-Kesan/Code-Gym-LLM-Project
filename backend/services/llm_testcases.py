from .query_llm import chat_with_llm

def generate_test_cases(question_title: str, question_description: str, user_code: str) -> str:
    prompt = f"""
    You are a Python testing expert.

    PROBLEM:
    Title: {question_title}
    Description: {question_description}

    STUDENT CODE:
    {user_code}

    TASK:
    Generate exactly 2-3 additional test cases focusing on edge cases and performance issues.
    Follow the given format strictly. Don't give any extra explanations.

    FORMAT (use exactly this format with no additional explanations):

    TEST CASE 1:
    Input: [provide input]
    Expected Output: [provide expected output]
    Focus: [one brief phrase describing what this test checks]

    TEST CASE 2:
    Input: [provide input]
    Expected Output: [provide expected output]
    Focus: [one brief phrase describing what this test checks]

    TEST CASE 3 (optional):
    Input: [provide input]
    Expected Output: [provide expected output]
    Focus: [one brief phrase describing what this test checks]
    """
    response = chat_with_llm(prompt)
    return response
