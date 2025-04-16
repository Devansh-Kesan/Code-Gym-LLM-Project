from .query_llm import chat_with_llm
import mlflow

def generate_progressive_hints(question_title: str, question_description: str, user_code: str) -> str:
    with mlflow.start_run(run_name="LLM_Feature: Progressive Hints"):
        # Log input parameters
        mlflow.log_param("feature", "generate_progressive_hints")
        mlflow.log_param("question_title", question_title)

        # Log artifacts (inputs as files)
        mlflow.log_text(question_description, "question_description.txt")
        mlflow.log_text(user_code, "user_code.py")

        # Create prompt
        prompt = f"""
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

        FORMAT (use exactly this structure and don't give any introduction or conclusion just give the hints):
        Hint 1: [Brief conceptual guidance]

        Hint 2: [Specific approach suggestion]

        Hint 3: [Targeted implementation advice without revealing full solution]
        """

        # Get LLM response
        response = chat_with_llm(prompt)

        # Log output
        mlflow.log_text(response, "llm_hints_response.txt")
        mlflow.log_metric("response_length", len(response))

        return response
