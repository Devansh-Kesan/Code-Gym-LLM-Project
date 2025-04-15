from .query_llm import chat_with_llm

def scaffold_question(question_title: str, question_description: str, user_code: str) -> str:
    prompt = f"""
    You are a computer science instructor helping a student understand problem-solving steps.

    PROBLEM:
    Title: {question_title}
    Description: {question_description}

    STUDENT CODE:
    {user_code}

    TASK:
    Break down the problem-solving process into 3-5 clear conceptual steps that will guide the student without giving away the full solution.

    FORMAT (use exactly this format with no additional text):

    Problem-Solving Framework

    Step 1: [Brief title for first step]
    [1-2 sentence explanation of this conceptual step]

    Step 2: [Brief title for second step]
    [1-2 sentence explanation of this conceptual step]

    Step 3: [Brief title for third step]
    [1-2 sentence explanation of this conceptual step]

    Step 4 (if needed): [Brief title for fourth step]
    [1-2 sentence explanation of this conceptual step]

    Step 5 (if needed): [Brief title for fifth step]
    [1-2 sentence explanation of this conceptual step]
    """
    response = chat_with_llm(prompt)
    
    return response
