import ollama
import mlflow

def chat_with_llm(prompt: str, model: str = "qwen2.5") -> str:
    with mlflow.start_run(run_name="LLM_Model_Response", nested=True):  # Use nested=True to avoid conflicts with parent runs
        mlflow.log_param("llm_model", model)
        mlflow.log_text(prompt, "llm_input_prompt.txt")
        
        response = ollama.chat(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        output = response["message"]["content"]
        
        mlflow.log_text(output, "llm_response_output.txt")
        mlflow.log_metric("response_length", len(output))
        
        print(output)
        return output
