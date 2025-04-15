from prefect import flow, task
import os
import yaml
import json
import uuid
import subprocess
from pathlib import Path
import textwrap
import shutil

@task(name="setup_directories")
def setup_directories(submission_id: str):
    current_dir = os.getcwd()
    submissions_dir = os.path.join(current_dir, "submissions")

    # Empty the submissions folder if it exists
    if os.path.exists(submissions_dir):
        for item in os.listdir(submissions_dir):
            item_path = os.path.join(submissions_dir, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
    else:
        os.makedirs(submissions_dir, exist_ok=True)

    base_dir = os.path.join(submissions_dir, f"submission_{submission_id}")
    code_dir = os.path.join(base_dir, "code")
    tests_dir = os.path.join(base_dir, "tests")
    results_dir = os.path.join(base_dir, "results")

    os.makedirs(code_dir, exist_ok=True)
    os.makedirs(tests_dir, exist_ok=True)
    os.makedirs(os.path.join(tests_dir, "expected_outputs"), exist_ok=True)
    os.makedirs(results_dir, exist_ok=True)

    return code_dir, tests_dir, results_dir

@task(name="write_user_code")
def write_user_code(code_dir: str, user_code: str):
    code_file = os.path.join(code_dir, "solution.py")
    with open(code_file, "w") as f:
        f.write(user_code)

@task(name="load_problem_config")
def load_problem_config(problem_id: str):
    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    for course in config.get("courses", []):
        for topic in course.get("topics", []):
            for question in topic.get("questions", []):
                if question.get("id") == problem_id:
                    return question, question.get("title", "")
    
    raise ValueError(f"Problem with ID {problem_id} not found in config")

@task(name="prepare_test_cases")
def prepare_test_cases(problem_config: dict, hidden: bool):
    test_cases_config = problem_config.get("test_cases", {})
    visible_cases = test_cases_config.get("visible_cases", [])
    hidden_cases = test_cases_config.get("hidden_cases", []) if hidden else []
    
    all_test_cases = []
    for i, test_case in enumerate(visible_cases):
        all_test_cases.append({
            "id": f"visible_{i}",
            "input": test_case.get("input", ""),
            "expected_output": test_case.get("expected_output", ""),
            "is_hidden": False
        })
    
    for i, test_case in enumerate(hidden_cases):
        all_test_cases.append({
            "id": f"hidden_{i}",
            "input": test_case.get("input", ""),
            "expected_output": test_case.get("expected_output", ""),
            "is_hidden": True
        })
    
    return all_test_cases

@task(name="generate_test_files")
def generate_test_files(tests_dir: str, all_test_cases: list, time_limit_seconds: int):
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
        
        test_file = os.path.join(tests_dir, f"test_{test_id}.py")
        with open(test_file, "w") as f:
            f.write(test_content)

        output_file = os.path.join(tests_dir, "expected_outputs", f"output_{test_id}.txt")
        with open(output_file, "w") as f:
            f.write(test_case["expected_output"])

@task(name="run_tests")
def run_tests(code_dir: str, tests_dir: str, results_dir: str):
    cmd = [
        "docker", "run", "--rm",
        "-v", f"{os.path.abspath(code_dir)}:/code:ro",
        "-v", f"{os.path.abspath(tests_dir)}:/tests:ro",
        "-v", f"{os.path.abspath(results_dir)}:/results",
        "code-gym-tester"
    ]
    
    process = subprocess.run(cmd, capture_output=True, text=True)
    return process

@task(name="process_results")
def process_results(results_dir: str, all_test_cases: list, problem_id: str, problem_title: str):
    results_file = os.path.join(results_dir, "results.json")
    try:
        with open(results_file, "r") as f:
            results = json.load(f)
        
        for test_result in results.get("test_results", []):
            if not test_result["passed"] and test_result.get("error"):
                error_msg = test_result["error"]
                lines = error_msg.splitlines()
                if len(lines) >= 3:
                    last_line = lines[-3]
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
        
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)
        
        return results
    except FileNotFoundError:
        return {
            "error": "No results file found",
            "passed": 0,
            "failed": len(all_test_cases),
            "total": len(all_test_cases),
            "problem_id": problem_id,
            "problem_title": problem_title
        }

@flow(name="process_code_submission")
def process_code_submission_flow(user_code: str, problem_id: str, hidden: bool = True):
    try:
        submission_id = str(uuid.uuid4())
        
        # Setup directories
        code_dir, tests_dir, results_dir = setup_directories(submission_id)
        
        # Write user code
        write_user_code(code_dir, user_code)
        
        # Load problem configuration
        problem_config, problem_title = load_problem_config(problem_id)
        
        # Prepare test cases
        all_test_cases = prepare_test_cases(problem_config, hidden)
        
        # Generate test files
        time_limit_seconds = problem_config.get("time_limit_seconds", 5)
        generate_test_files(tests_dir, all_test_cases, time_limit_seconds)
        
        # Run tests
        run_tests(code_dir, tests_dir, results_dir)
        
        # Process results
        return process_results(results_dir, all_test_cases, problem_id, problem_title)
        
    except Exception as e:
        return {
            "error": f"Error processing submission: {str(e)}",
            "passed": 0,
            "failed": 0,
            "total": 0
        }