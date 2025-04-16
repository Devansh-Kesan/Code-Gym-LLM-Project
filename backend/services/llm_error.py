from .query_llm import chat_with_llm
from typing import List

def generate_error_explanation(error_list: List[dict],question_title: str, question_description: str, user_code: str) -> str:
    prompt = f"""
    You are a Python error analyst.

    PROBLEM:
    Title: {question_title}
    Description: {question_description}

    STUDENT CODE:
    {user_code}

    "Errors":
    {error_list}
    
    TASK:
    Explain the errors according to the testcases occured for the question and also identify and explain any runtime or compile-time errors in the code. Focus only on explaining what the errors mean in simple terms.

    FORMAT (use exactly this format):

    Error Detected
    [Name of the error type]

    Error Explanation
    [2-3 sentences explaining what the error means in plain language]

    Cause
    [1-2 sentences identifying the specific part of code causing the error]
    
    Fix
    [Brief fix to correct the errors. Don't give the code, just give an idea.]

    """
    response = chat_with_llm(prompt)
    return response