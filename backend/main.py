"""FastAPI backend for code submission processing and LLM services."""

import json
from pathlib import Path
from typing import Any

import yaml
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from js_submission_processor import process_js_submission_flow
from services.llm_error import generate_error_explanation
from services.llm_hint import generate_progressive_hints
from services.llm_review import generate_code_review
from services.llm_scaffold import scaffold_question
from services.llm_testcases import generate_test_cases
from services.pydantic_models import LLMRequest, RunCodeRequest
from submission_processor import process_code_submission_flow

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

courses_data: dict[str, Any] = {}
questions_data: dict[str, Any] = {}


def load_config(path: str = "config.yaml") -> None:
    """Load course and question data from config file.

    Args:
        path: Path to the config file

    """
    global courses_data, questions_data

    with Path(path).open(encoding="utf-8") as file:
        config = yaml.safe_load(file)

    for course in config.get("courses", []):
        course_id = course["id"]
        courses_data[course_id] = course

        for topic in course.get("topics", []):
            for question in topic.get("questions", []):
                qid = question["id"]
                questions_data[qid] = question


load_config()


def get_latest_submission_error() -> dict[str, Any] | None:
    """Get error from the most recent submission.

    Returns:
        Dictionary containing error details or None if no error found

    """
    submissions_dir = Path("submissions")
    submission_folders = [
        f for f in submissions_dir.iterdir()
        if f.is_dir() and f.name.startswith("submission")
    ]

    if not submission_folders:
        return None

    latest_submission = max(submission_folders, key=lambda f: f.stat().st_mtime)
    results_file = latest_submission / "results" / "results.json"

    if not results_file.exists():
        return None

    with results_file.open(encoding="utf-8") as f:
        return json.load(f)


@app.get("/debug")
def debug() -> dict[str, Any]:
    """Debug endpoint to return all questions data."""
    return questions_data


@app.get("/courses")
def get_courses() -> list[dict[str, Any]]:
    """Get list of all courses."""
    return list(courses_data.values())


@app.get("/courses/{course_id}")
def get_course(course_id: str) -> dict[str, Any]:
    """Get details for a specific course.

    Args:
        course_id: ID of the course to retrieve

    """
    course = courses_data.get(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@app.get("/courses/{course_id}/topics")
def get_topics(course_id: str) -> list[dict[str, Any]]:
    """Get all topics for a course.

    Args:
        course_id: ID of the course

    """
    course = courses_data.get(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course.get("topics", [])


@app.get("/courses/{course_id}/topics/{topic_id}")
def get_topic(course_id: str, topic_id: str) -> dict[str, Any]:
    """Get details for a specific topic.

    Args:
        course_id: ID of the course
        topic_id: ID of the topic

    """
    course = courses_data.get(course_id)
    topic = next(
        (t for t in course.get("topics", []) if t["topic_id"] == topic_id),
        None,
    )
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic


@app.get("/courses/{course_id}/topics/{topic_id}/questions/{question_id}")
def get_question(
    course_id: str,
    topic_id: str,
    question_id: str,
) -> dict[str, Any]:
    """Get details for a specific question.

    Args:
        course_id: ID of the course
        topic_id: ID of the topic
        question_id: ID of the question

    """
    question = questions_data.get(question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question


@app.post("/llm/hint")
def get_hint(request: LLMRequest) -> dict[str, list[str]]:
    """Get progressive hints for a coding problem.

    Args:
        request: Contains question details and user code

    """
    hints = generate_progressive_hints(
        question_title=request.title,
        question_description=request.description,
        user_code=request.code,
    )
    return {"hints": hints}


@app.post("/llm/explain-error")
def get_error_explanation(request: LLMRequest) -> dict[str, str]:
    """Get explanations for errors in user code.

    Args:
        request: Contains question details and user code

    """
    error = get_latest_submission_error()
    if not error:
        return {
            "explanations": "Please run the code at least once to see the error.",
        }

    if error["problem_title"] != request.title:
        return {
            "explanations": "Please run the code at least once to see the error.",
        }

    test_cases = questions_data[error["problem_id"]]["test_cases"]["visible_cases"]
    failed_tests = []
    for test_case, result in zip(test_cases, error["test_results"], strict=False):
        if not result["passed"]:
            result["input"] = test_case["input"]
            failed_tests.append(result)

    explanations = generate_error_explanation(
        error_list=failed_tests,
        question_title=request.title,
        question_description=request.description,
        user_code=request.code,
    )
    return {"explanations": explanations}


@app.post("/llm/test-cases")
def get_test_cases(request: LLMRequest) -> dict[str, list[str]]:
    """Generate test cases for a coding problem.

    Args:
        request: Contains question details and user code

    """
    test_cases = generate_test_cases(
        question_title=request.title,
        question_description=request.description,
        user_code=request.code,
    )
    return {"test_cases": test_cases}


@app.post("/llm/code-review")
def get_code_review(request: LLMRequest) -> dict[str, str]:
    """Get code review for user's solution.

    Args:
        request: Contains question details and user code

    """
    review = generate_code_review(
        question_title=request.title,
        question_description=request.description,
        user_code=request.code,
    )
    return {"review": review}


@app.post("/llm/question-scaffold")
def get_question_scaffolding(request: LLMRequest) -> dict[str, str]:
    """Get scaffolding for a coding problem.

    Args:
        request: Contains question details and user code

    """
    scaffold = scaffold_question(
        question_title=request.title,
        question_description=request.description,
        user_code=request.code,
    )
    return {"scaffold_data": scaffold}


@app.post("/run-code")
def run_python_code(request: RunCodeRequest) -> dict[str, Any]:
    """Run Python code with visible test cases.

    Args:
        request: Contains user code and question ID

    """
    return process_code_submission_flow(
        user_code=request.code,
        problem_id=request.question_id,
        hidden=False,
    )


@app.post("/run-code-all")
def run_python_code_all_tests(request: RunCodeRequest) -> dict[str, Any]:
    """Run Python code with all test cases (including hidden).

    Args:
        request: Contains user code and question ID

    """
    return process_code_submission_flow(
        user_code=request.code,
        problem_id=request.question_id,
        hidden=True,
    )


@app.post("/run-code-js")
def run_javascript_code(request: RunCodeRequest) -> dict[str, Any]:
    """Run JavaScript code with visible test cases.

    Args:
        request: Contains user code and question ID

    """
    return process_js_submission_flow(
        user_code=request.code,
        problem_id=request.question_id,
        hidden=False,
    )


@app.post("/run-code-all-js")
def run_javascript_code_all_tests(request: RunCodeRequest) -> dict[str, Any]:
    """Run JavaScript code with all test cases (including hidden).

    Args:
        request: Contains user code and question ID

    """
    return process_js_submission_flow(
        user_code=request.code,
        problem_id=request.question_id,
        hidden=True,
    )


if __name__ == "__main__":
    import uvicorn

    # Run the FastAPI app on a custom port
    uvicorn.run(app, host="0.0.0.0", port=8080)