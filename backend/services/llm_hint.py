from .query_llm import chat_with_llm

def generate_progressive_hints(question_title: str, question_description: str, user_code: str) -> str:
    prompt = f"""
    You are a helpful coding assistant. A student is trying to solve the following problem:

    Title: {question_title}

    Description: {question_description}

    Here is their current solution attempt: {user_code}

    Instead of giving the solution, provide three tiered progressive hints that guide them toward solving the problem. 
    Start from a high-level idea and gradually move toward more detailed guidance.
    Do NOT reveal the exact solution.

    Respond in this format:

    Hint 1: ...
    Hint 2: ...
    Hint 3: ...
    """
    return chat_with_llm(prompt)
