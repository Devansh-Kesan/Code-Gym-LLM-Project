from .query_llm import chat_with_llm
import mlflow
from prefect import flow, task
from typing import Dict

@task(name="prepare_testcase_prompt")
def prepare_prompt(question_title: str, question_description: str, user_code: str) -> str:
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
    return prompt

@task(name="log_testcase_metrics")
def log_mlflow_data(question_title: str, question_description: str, 
                    user_code: str, response: str) -> None:
    mlflow.log_param("feature", "generate_test_cases")
    mlflow.log_param("question_title", question_title)
    mlflow.log_text(question_description, "question_description.txt")
    mlflow.log_text(user_code, "user_code.py")
    mlflow.log_text(response, "llm_generated_test_cases.txt")
    mlflow.log_metric("response_length", len(response))

@flow(name="Generate Test Cases")
def generate_test_cases(question_title: str, question_description: str, user_code: str) -> str:
    with mlflow.start_run(run_name="LLM_Feature: Generate Test Cases"):
        # Prepare the prompt
        prompt = prepare_prompt(question_title, question_description, user_code)
        
        # Get LLM response
        response = chat_with_llm(prompt)
        
        # Log MLflow metrics and data
        log_mlflow_data(question_title, question_description, user_code, response)
        
        return response