from .query_llm import chat_with_llm
import mlflow

def scaffold_question(question_title: str, question_description: str, user_code: str) -> str:
    with mlflow.start_run(run_name="LLM_Feature: Scaffold Question"):
        # Log basic parameters
        mlflow.log_param("feature", "scaffold_question")
        mlflow.log_param("question_title", question_title)

        # Log input artifacts
        mlflow.log_text(question_description, "question_description.txt")
        mlflow.log_text(user_code, "user_code.py")

        # Build prompt
        prompt = f"""
        You are a computer science instructor helping a student understand problem-solving steps.

        PROBLEM:
        Title: {question_title}
        Description: {question_description}

        STUDENT CODE:
        {user_code}

        TASK:
        Break down the problem-solving process into 3-5 clear conceptual steps that will guide the student without giving away the full solution.

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

        # Get LLM output
        response = chat_with_llm(prompt)

        # Log LLM response and metrics
        mlflow.log_text(response, "llm_scaffold_response.txt")
        mlflow.log_metric("response_length", len(response))

        return response
