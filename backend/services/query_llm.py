"""LLM Query."""

import mlflow
import ollama
from prefect import flow, task


@task(name="query_llm_model",
      retries=3,
      retry_delay_seconds=2)
def query_model(prompt: str, model: str) -> str:
    """Query the LLM model with retry capability."""
    response = ollama.chat(
        model=model,
        messages=[
            {"role": "user", "content": prompt},
        ],
    )
    return response["message"]["content"]

@task(name="log_mlflow_metrics")
def log_mlflow_metrics(prompt: str, output: str, model: str) -> None:
    """Log metrics and artifacts to MLflow."""
    mlflow.log_param("llm_model", model)
    mlflow.log_text(prompt, "llm_input_prompt.txt")
    mlflow.log_text(output, "llm_response_output.txt")
    mlflow.log_metric("response_length", len(output))

@flow(name="LLM Chat Flow")
def chat_with_llm(prompt: str, model: str = "qwen2.5") -> str:
    """Chat with LLM and log results."""
    with mlflow.start_run(run_name="LLM_Model_Response", nested=True):
        # Query the model
        output = query_model(prompt, model)

        # Log metrics and artifacts
        log_mlflow_metrics(prompt, output, model)

        return output
