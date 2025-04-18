"""Module for processing code submissions with Docker."""

import json
import shutil
import subprocess
import textwrap
import uuid
from pathlib import Path
from typing import Any

import yaml
from prefect import flow, task


@task(name="setup_directories")
def setup_directories(submission_id: str) -> tuple[Path, Path, Path]:
    """Set up directories for submission processing."""
    current_dir = Path.cwd()
    submissions_dir = current_dir / "submissions"

    # Empty the submissions folder if it exists
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

    code_dir.mkdir(parents=True, exist_ok=True)
    tests_dir.mkdir(parents=True, exist_ok=True)
    (tests_dir / "expected_outputs").mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)

    return code_dir, tests_dir, results_dir


@task(name="write_user_code")
def write_user_code(code_dir: Path, user_code: str) -> None:
    """Write user code to a file."""
    code_file = code_dir / "solution.py"
    with code_file.open("w", encoding="utf-8") as f:
        f.write(user_code)


@task(name="load_problem_config")
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

    error_msg = f"Problem with ID {problem_id} not found in config"
    raise ValueError(error_msg)


@task(name="prepare_test_cases")
def prepare_test_cases(
    problem_config: dict[str, Any],
    *,  # Force keyword arguments after this point
    hidden: bool,
) -> list[dict[str, Any]]:
    """Prepare test cases for execution."""
    test_cases_config = problem_config.get("test_cases", {})
    visible_cases = test_cases_config.get("visible_cases", [])
    hidden_cases = test_cases_config.get("hidden_cases", []) if hidden else []

    all_test_cases = []
    for i, test_case in enumerate(visible_cases):
        all_test_cases.append({
            "id": f"visible_{i}",
            "input": test_case.get("input", ""),
            "expected_output": test_case.get("expected_output", ""),
            "is_hidden": False,
        })

    for i, test_case in enumerate(hidden_cases):
        all_test_cases.append({
            "id": f"hidden_{i}",
            "input": test_case.get("input", ""),
            "expected_output": test_case.get("expected_output", ""),
            "is_hidden": True,
        })

    return all_test_cases


@task(name="generate_test_files")
def generate_test_files(
    tests_dir: Path,
    all_test_cases: list[dict[str, Any]],
    time_limit_seconds: int,
) -> None:
    """Generate test files for each test case."""
    for test_case in all_test_cases:
        test_id = test_case["id"]
        test_content = textwrap.dedent(f"""
        import sys
        import io
        import runpy
        import pytest
        import json
        import signal
        sys.path.append('/code')

        class TimeoutException(Exception):
            pass

        def timeout_handler(signum, frame):
            raise TimeoutException("Test case exceeded time limit")

        signal.signal(signal.SIGALRM, timeout_handler)

        def test_{test_id}():
            signal.alarm({time_limit_seconds})
            captured_output = io.StringIO()
            sys.stdout = captured_output
            sys.stdin = io.StringIO('''{test_case["input"]}''')
            try:
                import solution
                if hasattr(solution, 'main'):
                    solution.main()
                else:
                    runpy.run_module('solution', run_name='__main__')
            except TimeoutException:
                signal.alarm(0)
                pytest.fail("Time Limit Exceeded")
            except Exception as e:
                signal.alarm(0)
                pytest.fail(type(e).__name__)
            else:
                signal.alarm(0)
            finally:
                sys.stdout = sys.__stdout__
            output = captured_output.getvalue().strip()
            expected = '''{test_case["expected_output"]}'''.strip()
            if output != expected:
                error_info = {{
                    "error_type": "AssertionError",
                    "expected": expected,
                    "actual": output
                }}
                pytest.fail(json.dumps(error_info))
        """)

        test_file = tests_dir / f"test_{test_id}.py"
        with test_file.open("w", encoding="utf-8") as f:
            f.write(test_content)

        output_file = tests_dir / "expected_outputs" / f"output_{test_id}.txt"
        with output_file.open("w", encoding="utf-8") as f:
            f.write(test_case["expected_output"])


@task(name="run_tests")
def run_tests(
    code_dir: Path,
    tests_dir: Path,
    results_dir: Path,
) -> subprocess.CompletedProcess:
    """Run tests in Docker container.

    Security note: The command is constructed from:
    - Hardcoded strings ("docker", "run", etc.)
    - Resolved absolute paths from the submission process
    - A constant container name ("code-gym-tester")
    All components are trusted and not user-provided.
    """
    cmd = [
        "docker", "run", "--rm",
        "-v", f"{code_dir.resolve()}:/code:ro",
        "-v", f"{tests_dir.resolve()}:/tests:ro",
        "-v", f"{results_dir.resolve()}:/results",
        "code-gym-tester",
    ]
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


@task(name="process_results")
def process_results(
    results_dir: Path,
    all_test_cases: list[dict[str, Any]],
    problem_id: str,
    problem_title: str,
) -> dict[str, Any]:
    """Process test results from Docker execution."""
    results_file = results_dir / "results.json"
    try:
        with results_file.open(encoding="utf-8") as f:
            results = json.load(f)

        for test_result in results.get("test_results", []):
            if not test_result["passed"] and test_result.get("error"):
                error_msg = test_result["error"]
                lines = error_msg.splitlines()
                t = 3
                if len(lines) >= t:
                    last_line = lines[-t]
                    if "Failed: " in last_line:
                        json_str = last_line.split("Failed: ", 1)[1].strip()
                        try:
                            error_data = json.loads(json_str)
                            if error_data.get("error_type") == "AssertionError":
                                test_result["expected"] = error_data["expected"]
                                test_result["actual"] = error_data["actual"]
                                test_result["error"] = "Wrong Answer"
                        except json.JSONDecodeError:
                            test_result["error"] = json_str

        results["problem_id"] = problem_id
        results["problem_title"] = problem_title

        with results_file.open("w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

    except FileNotFoundError:
        results = {
            "error": "No results file found",
            "passed": 0,
            "failed": len(all_test_cases),
            "total": len(all_test_cases),
            "problem_id": problem_id,
            "problem_title": problem_title,
        }

    return results


@flow(name="process_code_submission")
def process_code_submission_flow(
    user_code: str,
    problem_id: str,
    *,  # Force keyword arguments after this point
    hidden: bool = True,
) -> dict[str, Any]:
    """Process code submission flow."""
    try:
        submission_id = str(uuid.uuid4())

        # Setup directories
        code_dir, tests_dir, results_dir = setup_directories(submission_id)

        # Write user code
        write_user_code(code_dir, user_code)

        # Load problem configuration
        problem_config, problem_title = load_problem_config(problem_id)

        # Prepare test cases
        all_test_cases = prepare_test_cases(problem_config, hidden=hidden)

        # Generate test files
        time_limit_seconds = problem_config.get("time_limit_seconds", 5)
        generate_test_files(tests_dir, all_test_cases, time_limit_seconds)

        # Run tests
        run_tests(code_dir, tests_dir, results_dir)

        # Process results
        return process_results(results_dir, all_test_cases, problem_id, problem_title)

    except (ValueError, RuntimeError) as e:
        return {
            "error": f"Error processing submission: {e!s}",
            "passed": 0,
            "failed": 0,
            "total": 0,
        }
