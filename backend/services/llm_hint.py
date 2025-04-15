from .query_llm import chat_with_llm

def generate_progressive_hints(question_title: str, question_description: str, user_code: str) -> str:
    prompt = f"""
    You are a programming instructor.

    PROBLEM:
    Title: {question_title}
    Description: {question_description}

    STUDENT CODE:
    {user_code}

    TASK:
    Generate three progressive hints for the student. Each hint should be:
    - Starting on new line.
    - Concise (max 1-2 sentences).
    - Direct and specific.
    - Numbered as shown in the format below.

    FORMAT (use exactly this structure and don't give any introduction or conclusion just give the hints):
    Hint 1: [Brief conceptual guidance]

    Hint 2: [Specific approach suggestion]

    Hint 3: [Targeted implementation advice without revealing full solution]
    """
    return chat_with_llm(prompt)
