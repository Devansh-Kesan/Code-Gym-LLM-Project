from .query_llm import chat_with_llm
import mlflow
from prefect import flow, task
from typing import Dict

@task(name="prepare_review_prompt")
def prepare_prompt(question_title: str, question_description: str, user_code: str) -> str:
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
    return prompt

@task(name="log_review_metrics")
def log_mlflow_data(question_title: str, question_description: str, 
                    user_code: str, response: str) -> None:
    mlflow.log_param("feature", "generate_code_review")
    mlflow.log_param("question_title", question_title)
    mlflow.log_text(question_description, "question_description.txt")
    mlflow.log_text(user_code, "user_code.py")
    mlflow.log_text(response, "llm_code_review_response.txt")
    mlflow.log_metric("response_length", len(response))

@flow(name="Generate Code Review")
def generate_code_review(question_title: str, question_description: str, user_code: str) -> str:
    with mlflow.start_run(run_name="LLM_Feature: Code Review"):
        # Prepare the prompt
        prompt = prepare_prompt(question_title, question_description, user_code)
        
        # Get LLM response
        response = chat_with_llm(prompt)
        
        # Log MLflow metrics and data
        log_mlflow_data(question_title, question_description, user_code, response)
        
        return response