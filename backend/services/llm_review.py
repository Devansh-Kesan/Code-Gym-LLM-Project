from .query_llm import chat_with_llm

def generate_code_review(question_title: str, question_description: str, user_code: str) -> str:
    prompt = f"""
    You are a code reviewer evaluating student code.

    PROBLEM:
    Title: {question_title}
    Description: {question_description}

    STUDENT CODE:
    {user_code}

    TASK:
    Evaluate ONLY these three aspects of the solution.
    - Keep your response concise and direct.
    - Don't give any extra explanation or code just follow the FORMAT
    
    FORMAT (use exactly this structure):

    CORRECTNESS: [Explanation if issues exist]

    COMPLEXITY: [Time and Space complexity of the solution in Big O-notation]

    APPROACH: [Optimal or suboptimal, if suboptimal briefly suggest a better approach and don't give extra unrelated suggestions]
    """
    response = chat_with_llm(prompt)
    return response