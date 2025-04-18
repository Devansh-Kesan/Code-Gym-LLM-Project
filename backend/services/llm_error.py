"""LLM Error Explain Model."""

import mlflow

from .query_llm import chat_with_llm


def generate_error_explanation(error_list: list[dict],
                               question_title: str,
                               question_description: str,
                               user_code: str) -> str:
    """Generate error explanation."""
    with mlflow.start_run():
        # Log input parameters
        mlflow.log_param("feature", "explain_error")
        mlflow.log_param("question_title", question_title)
        mlflow.log_param("num_errors", len(error_list))

        # Log input artifacts
        mlflow.log_text(question_description, "question_description.txt")
        mlflow.log_text(user_code, "user_code.py")
        mlflow.log_text(str(error_list), "error_list.txt")

        # Construct prompt
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
        Explain the errors according to the testcases occurred for
        the question and also identify and
        explain any runtime or compile-time errors in the code.
        Focus only on explaining what the errors mean in simple terms.

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

        # Run LLM
        response = chat_with_llm(prompt)

        # Log response
        mlflow.log_text(response, "llm_response.txt")
        mlflow.log_metric("response_length", len(response))

        return response
