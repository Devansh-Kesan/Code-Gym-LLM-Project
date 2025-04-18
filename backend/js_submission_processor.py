"""Processing JavaScript code submissions with Docker and MLflow integration."""

import json
import shutil
import subprocess
import textwrap
import uuid
from pathlib import Path
from typing import Any

import mlflow
import yaml
from prefect import flow, task


@task(name="log_submission_metrics")
def log_submission_metrics(
    results: dict[str, Any],
    user_code: str,
    problem_id: str,
) -> None:
    """Log metrics and artifacts for a submission."""
    mlflow.log_param("problem_id", problem_id)
    mlflow.log_param("total_tests", results["total"])

    # Log metrics
    mlflow.log_metric("tests_passed", results["passed"])
    mlflow.log_metric("tests_failed", results["failed"])
    success_rate = (
        results["passed"] / results["total"] if results["total"] > 0 else 0
    )
    mlflow.log_metric("success_rate", success_rate)

    # Log artifacts
    mlflow.log_text(user_code, "submitted_code.js")
    if "error" in results:
        mlflow.log_text(results["error"], "error.txt")

    # Log test results
    if "test_results" in results:
        test_results_str = json.dumps(results["test_results"], indent=2)
        mlflow.log_text(test_results_str, "test_results.json")


@task(name="setup_js_directories")
def setup_directories(submission_id: str) -> tuple[Path, Path, Path]:
    """Set up directories for submission processing."""
    submissions_dir = Path("submissions")
    if submissions_dir.exists():
        for item in submissions_dir.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
    else:
        submissions_dir.mkdir(exist_ok=True)

    base_dir = submissions_dir / f"submission_{submission_id}"
    code_dir = base_dir / "code"
    tests_dir = base_dir / "tests"
    results_dir = base_dir / "results"

    for directory in (code_dir, tests_dir, results_dir):
        directory.mkdir(parents=True, exist_ok=True)

    return code_dir, tests_dir, results_dir


@task(name="write_js_code")
def write_user_code(code_dir: Path, user_code: str) -> None:
    """Write user code to a file."""
    code_file = code_dir / "solution.js"
    with code_file.open("w", encoding="utf-8") as f:
        f.write(user_code)


@task(name="load_js_problem_config")
def load_problem_config(problem_id: str) -> tuple[dict[str, Any], str]:
    """Load problem configuration from YAML file."""
    config_path = Path(__file__).parent / "config.yaml"
    with config_path.open(encoding="utf-8") as f:
        config = yaml.safe_load(f)

    for course in config.get("courses", []):
        for topic in course.get("topics", []):
            for question in topic.get("questions", []):
                if question.get("id") == problem_id:
                    return question, question.get("title", "")

    error_msg = f"Problem with ID {problem_id} not found"
    raise ValueError(error_msg)


@task(name="prepare_js_test_cases")
def prepare_test_cases(
    problem_config: dict[str, Any],
    *,  # Force keyword arguments after this point
    hidden: bool,
) -> tuple[list[dict[str, Any]], int]:
    """Prepare test cases for execution."""
    visible_test_cases = problem_config["test_cases"]["visible_cases"]
    hidden_test_cases = []

    if hidden and "hidden_cases" in problem_config["test_cases"]:
        hidden_test_cases = problem_config["test_cases"]["hidden_cases"]

    all_test_cases = (
        visible_test_cases + hidden_test_cases if hidden else visible_test_cases
    )
    return all_test_cases, len(visible_test_cases)


@task(name="generate_jest_test_files")
def generate_test_files(
    tests_dir: Path,
    test_cases: list[dict[str, Any]],
    visible_cases_count: int,
) -> None:
    """Generate Jest test files for each test case."""
    for i, test_case in enumerate(test_cases):
        is_hidden = i >= visible_cases_count
        test_id = f"hidden_{i - visible_cases_count}" if is_hidden else f"visible_{i}"

        input_data = json.dumps(test_case["input"])[1:-1] + "\\n"
        expected_output = json.dumps(test_case["expected_output"])[1:-1]

        test_content = textwrap.dedent(f"""\
            const {{ spawnSync }} = require('child_process');
            const path = require('path');

            describe('Test {test_id}', () => {{
                it('should match expected output', () => {{
                    const input = '{input_data}';
                    const expected = '{expected_output}';
                    const result = spawnSync('node', [
                        path.join('/code', 'solution.js')
                    ], {{
                        input,
                        timeout: 5000,
                        encoding: 'utf-8'
                    }});

                    if (result.error) {{
                        if (result.error.code === 'ETIMEDOUT') {{
                            throw new Error('Time Limit Exceeded');
                        }}
                        throw result.error;
                    }}

                    if (result.status !== 0) {{
                        throw new Error(`Process exited with code ${{result.status}}`);
                    }}

                    console.log("Test Result:");
                    console.log(JSON.stringify(result, null, 2));
                    const output = result.stdout.trim().split('\\n').pop();
                    expect(output).toBe(expected);
                }});
            }});
        """)

        test_file = tests_dir / f"test_{test_id}.test.js"
        with test_file.open("w", encoding="utf-8") as f:
            f.write(test_content)


@task(name="run_js_tests")
def run_tests(
    code_dir: Path,
    tests_dir: Path,
    results_dir: Path,
) -> subprocess.CompletedProcess:
    """Run tests in Docker container."""
    cmd = [
        "docker",
        "run",
        "--rm",
        "-v", f"{code_dir.absolute()}:/code:ro",
        "-v", f"{tests_dir.absolute()}:/tests:ro",
        "-v", f"{results_dir.absolute()}:/results",
        "code-gym-tester-js",
    ]
    # Security note: cmd is constructed from trusted paths and constant strings
    return subprocess.run(cmd, capture_output=True,
                         text=True, encoding="utf-8", check=False)


@task(name="process_js_results")
def process_results(
    results_dir: Path,
    test_cases: list[dict[str, Any]],
    problem_id: str,
    problem_title: str,
) -> dict[str, Any]:
    """Process test results from Docker execution."""
    results_file = results_dir / "results.json"

    if not results_file.exists():
        error_result = {
            "error": "Results file not created by Docker container",
            "passed": 0,
            "failed": len(test_cases),
            "total": len(test_cases),
        }
        with results_file.open("w", encoding="utf-8") as f:
            json.dump(error_result, f, indent=2)
        return error_result

    with results_file.open(encoding="utf-8") as f:
        results = json.load(f)

    processed_results = {
        "passed": results.get("numPassedTests", 0),
        "failed": results.get("numFailedTests", 0),
        "total": results.get("numTotalTests", 0),
        "test_results": [],
        "problem_id": problem_id,
        "problem_title": problem_title,
    }

    for test_result in results.get("testResults", []):
        for assertion in test_result.get("assertionResults", []):
            test_path = assertion.get("ancestorTitles", "")[0]
            test_file_name = test_path
            is_hidden = "hidden_" in test_file_name

            test_info = {
                "test_id": test_file_name,
                "passed": assertion["status"] == "passed",
                "is_hidden": is_hidden,
            }

            if assertion["status"] == "failed":
                failure_messages = assertion.get("failureMessages", [])
                if failure_messages:
                    failure_message = failure_messages[0]
                else:
                    "Unknown error"
                test_info["error"] = failure_message
                if "Time Limit Exceeded" in failure_message:
                    test_info["error"] = "Time Limit Exceeded"
                elif "expected" in failure_message.lower():
                    lines = failure_message.split("\n")
                    expected = next(
                        (line.split(": ")[1] for line in lines if "Expected:" in line),
                        "N/A",
                    )
                    received = next(
                        (line.split(": ")[1] for line in lines if "Received:" in line),
                        "N/A",
                    )
                    test_info["error"] = "Wrong Answer"
                    test_info["expected"] = expected.strip('"')
                    test_info["actual"] = received.strip('"')

            processed_results["test_results"].append(test_info)

    with results_file.open("w", encoding="utf-8") as f:
        json.dump(processed_results, f, indent=2)

    return processed_results


@flow(name="process_js_submission")
def process_js_submission_flow(
    user_code: str,
    problem_id: str,
    *,  # Force keyword arguments after this point
    hidden: bool = False,
) -> dict[str, Any]:
    """Process JavaScript submission with Docker and MLflow logging."""
    try:
        with mlflow.start_run(run_name=f"JS_Submission_{problem_id}"):
            submission_id = str(uuid.uuid4())

            # Setup directories
            code_dir, tests_dir, results_dir = setup_directories(submission_id)

            # Write user code
            write_user_code(code_dir, user_code)

            # Load problem configuration
            problem_config, problem_title = load_problem_config(problem_id)

            # Prepare test cases
            test_cases, visible_cases_count = prepare_test_cases(
                problem_config,
                hidden=hidden,
            )

            # Generate test files
            generate_test_files(tests_dir, test_cases, visible_cases_count)

            # Run tests
            run_tests(code_dir, tests_dir, results_dir)

            # Process results
            results = process_results(
                results_dir,
                test_cases,
                problem_id,
                problem_title,
            )

            # Log metrics and artifacts
            log_submission_metrics(results, user_code, problem_id)

            return results

    except (ValueError, RuntimeError) as exc:
        error_result = {
            "error": f"Error processing submission: {exc!s}",
            "passed": 0,
            "failed": 0,
            "total": 0,
        }
        with mlflow.start_run(run_name=f"JS_Submission_Error_{problem_id}"):
            log_submission_metrics(error_result, user_code, problem_id)
        return error_result


if __name__ == "__main__":
    sample_code = """console.log("Hello, World!");"""

    # To run with only visible test cases
    result_visible = process_js_submission_flow(
        sample_code,
        "js-print-hello",
        hidden=False,
    )

    # To run with both visible and hidden test cases
    result_all = process_js_submission_flow(
        sample_code,
        "js-print-hello",
        hidden=True,
    )
