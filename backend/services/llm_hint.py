"""Progressive LLM Hint Module."""

import mlflow
from prefect import flow, task

from .query_llm import chat_with_llm


@task(name="prepare_prompt")
def prepare_prompt(question_title: str,
                   question_description: str, user_code: str) -> str:
    """Prepare Prompt for the LLM."""
    return  f"""
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

    FORMAT (use exactly this structure and don't give any
    introduction or conclusion just give the hints):
    Hint 1: [Brief conceptual guidance]

    Hint 2: [Specific approach suggestion]

    Hint 3: [Targeted implementation advice without revealing full solution]
    """

@task(name="log_mlflow_metrics")
def log_mlflow_data(question_title: str, question_description: str,
                    user_code: str, response: str) -> None:
    """Log mlflow data."""
    mlflow.log_param("feature", "generate_progressive_hints")
    mlflow.log_param("question_title", question_title)
    mlflow.log_text(question_description, "question_description.txt")
    mlflow.log_text(user_code, "user_code.py")
    mlflow.log_text(response, "llm_hints_response.txt")
    mlflow.log_metric("response_length", len(response))

@flow(name="Generate Progressive Hints")
def generate_progressive_hints(question_title: str,
                               question_description: str,
                               user_code: str) -> str:
    """Generate three progressive hints for the problem."""
    with mlflow.start_run(run_name="LLM_Feature: Progressive Hints"):
        # Prepare the prompt
        prompt = prepare_prompt(question_title, question_description, user_code)

        # Get LLM response
        response = chat_with_llm(prompt)

        # Log MLflow metrics and data
        log_mlflow_data(question_title, question_description, user_code, response)

        return response
