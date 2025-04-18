"""Conceptual Scaffold Module."""

import mlflow
from prefect import flow, task

from .query_llm import chat_with_llm


@task(name="prepare_scaffold_prompt")
def prepare_prompt(question_title: str,
                   question_description: str, user_code: str) -> str:
    """Generate prompt for LLM."""
    return f"""
    You are a computer science instructor
    helping a student understand problem-solving steps.

    PROBLEM:
    Title: {question_title}
    Description: {question_description}

    STUDENT CODE:
    {user_code}

    TASK:
    Break down the problem-solving process into 3-5 clear conceptual
    steps that will guide the student without giving away the full solution.

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

@task(name="log_scaffold_metrics")
def log_mlflow_data(question_title: str, question_description: str,
                    user_code: str, response: str) -> None:
    """Log mlflow data."""
    mlflow.log_param("feature", "scaffold_question")
    mlflow.log_param("question_title", question_title)
    mlflow.log_text(question_description, "question_description.txt")
    mlflow.log_text(user_code, "user_code.py")
    mlflow.log_text(response, "llm_scaffold_response.txt")
    mlflow.log_metric("response_length", len(response))

@flow(name="Scaffold Question")
def scaffold_question(question_title: str,
                      question_description: str, user_code: str) -> str:
    """Write conceptual scaffolding of the question."""
    with mlflow.start_run(run_name="LLM_Feature: Scaffold Question"):
        # Prepare the prompt
        prompt = prepare_prompt(question_title, question_description, user_code)

        # Get LLM response
        response = chat_with_llm(prompt)

        # Log MLflow metrics and data
        log_mlflow_data(question_title, question_description, user_code, response)

        return response
