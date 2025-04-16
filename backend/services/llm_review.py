from .query_llm import chat_with_llm
import mlflow

def generate_code_review(question_title: str, question_description: str, user_code: str) -> str:
    with mlflow.start_run(run_name="LLM_Feature: Code Review"):
        # Log input parameters
        mlflow.log_param("feature", "generate_code_review")
        mlflow.log_param("question_title", question_title)

        # Log artifacts
        mlflow.log_text(question_description, "question_description.txt")
        mlflow.log_text(user_code, "user_code.py")

        # Create the prompt
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

        # Get LLM response
        response = chat_with_llm(prompt)

        # Log LLM response and metrics
        mlflow.log_text(response, "llm_code_review_response.txt")
        mlflow.log_metric("response_length", len(response))

        return response
