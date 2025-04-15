import os
import uuid
import subprocess
import yaml
import json
from pathlib import Path
import textwrap
import shutil

def process_code_submission(user_code, problem_id, hidden=False):
    """Process a JavaScript code submission by running it in a Docker container and storing results.

    Args:
        user_code (str): The JavaScript code to execute.
        problem_id (str): The ID of the problem to fetch test cases for.
        hidden (bool): Whether to include hidden test cases. Default is False.

    Returns:
        dict: Test results or error information.
    """
    try:
        # Empty the submissions folder if it exists
        submissions_dir = Path("submissions")
        if submissions_dir.exists():
            for item in submissions_dir.iterdir():
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
        else:
            submissions_dir.mkdir(exist_ok=True)

        # Set up directory structure
        submission_id = str(uuid.uuid4())
        base_dir = Path("submissions") / f"submission_{submission_id}"
        code_dir = base_dir / "code"
        tests_dir = base_dir / "tests"
        results_dir = base_dir / "results"
        for directory in (code_dir, tests_dir, results_dir):
            directory.mkdir(parents=True, exist_ok=True)
        
        # Save the user's JavaScript code
        code_file = code_dir / "solution.js"
        with open(code_file, "w") as f:
            f.write(user_code)

        # Load problem configuration from config.yaml
        config_path = Path(__file__).parent / "config.yaml"
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        
        problem_config = None
        problem_title = None
        for course in config.get("courses", []):
            for topic in course.get("topics", []):
                for question in topic.get("questions", []):
                    if question.get("id") == problem_id:
                        problem_config = question
                        problem_title = question.get("title", "")
                        break
                if problem_config:
                    break
            if problem_config:
                break
        
        if not problem_config:
            raise ValueError(f"Problem with ID {problem_id} not found")

        # Get visible test cases
        visible_test_cases = problem_config["test_cases"]["visible_cases"]
        
        # Get hidden test cases if requested
        hidden_test_cases = []
        if hidden and "hidden_cases" in problem_config["test_cases"]:
            hidden_test_cases = problem_config["test_cases"]["hidden_cases"]
        
        # Combine test cases based on hidden parameter
        test_cases = visible_test_cases
        if hidden:
            test_cases = visible_test_cases + hidden_test_cases
        
        # Generate Jest test files for each test case
        for i, test_case in enumerate(test_cases):
            # Determine if this is a visible or hidden test
            is_hidden = i >= len(visible_test_cases)
            test_id = f"hidden_{i - len(visible_test_cases)}" if is_hidden else f"visible_{i}"
            
            # Properly format the input - make sure it ends with a newline for readline
            input_data = json.dumps(test_case["input"])[1:-1] + "\\n"
            expected_output = json.dumps(test_case["expected_output"])[1:-1]
            
            test_content = textwrap.dedent(f"""
                const {{ spawnSync }} = require('child_process');
                const path = require('path');

                describe('Test {test_id}', () => {{
                    it('should match expected output', () => {{
                        // Input with newline to trigger readline
                        const input = '{input_data}';
                        const expected = '{expected_output}';
                        
                        const result = spawnSync('node', [path.join('/code', 'solution.js')], {{ 
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

                        // Log the full result for debugging
                        console.log("Test Result:");
                        console.log(JSON.stringify(result, null, 2));
                        
                        const output = result.stdout.trim().split('\\n').pop();
                        expect(output).toBe(expected);
                    }});
                }});
            """)
            
            test_file = tests_dir / f"test_{test_id}.test.js"
            with open(test_file, "w") as f:
                f.write(test_content)

        # Run the Docker container with aligned Jest command
        cmd = [
            "docker", "run", "--rm",
            "-v", f"{code_dir.absolute()}:/code:ro",
            "-v", f"{tests_dir.absolute()}:/tests:ro",
            "-v", f"{results_dir.absolute()}:/results",
            "code-gym-tester-js"
        ]

        # Execute Docker command with detailed error capture
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        if process.returncode != 0 and not results_dir.joinpath("results.json").exists():
            error_result = {
                "error": f"Docker execution failed: {process.stderr}",
                "passed": 0,
                "failed": len(test_cases),
                "total": len(test_cases)
            }
            # Write error result to results.json
            with open(results_dir / "results.json", "w") as f:
                json.dump(error_result, f, indent=2)
            return error_result

        # Load and process the test results
        results_file = results_dir / "results.json"
        if not results_file.exists():
            error_result = {
                "error": "Results file not created by Docker container",
                "passed": 0,
                "failed": len(test_cases),
                "total": len(test_cases)
            }
            # Write error result to results.json
            with open(results_dir / "results.json", "w") as f:
                json.dump(error_result, f, indent=2)
            return error_result

        with open(results_file, "r") as f:
            results = json.load(f)

        # Process Jest results into a simplified format
        processed_results = {
            "passed": results.get("numPassedTests", 0),
            "failed": results.get("numFailedTests", 0),
            "total": results.get("numTotalTests", 0),
            "test_results": [],
            "problem_id": problem_id,
            "problem_title": problem_title
        }

        for test_result in results.get("testResults", []):
            for assertion in test_result.get("assertionResults", []):
                test_title = assertion["title"]
                # Extract test ID from test file path
                test_path = test_result.get("name", "")
                test_file_name = os.path.basename(test_path)
                test_id = test_file_name.replace("test_", "").replace(".test.js", "")
                
                # Determine if this is a hidden test
                is_hidden = test_id.startswith("hidden_")
                
                test_info = {
                    "test_id": test_id,
                    "passed": assertion["status"] == "passed",
                    "is_hidden": is_hidden
                }
                
                if assertion["status"] == "failed":
                    failure_message = assertion["failureMessages"][0] if assertion["failureMessages"] else "Unknown error"
                    test_info["error"] = failure_message
                    if "Time Limit Exceeded" in failure_message:
                        test_info["error"] = "Time Limit Exceeded"
                    elif "expected" in failure_message.lower():
                        lines = failure_message.split("\n")
                        expected = next((line.split(": ")[1] for line in lines if "Expected:" in line), "N/A")
                        received = next((line.split(": ")[1] for line in lines if "Received:" in line), "N/A")
                        test_info["error"] = "Wrong Answer"
                        test_info["expected"] = expected.strip('"')
                        test_info["actual"] = received.strip('"')
                
                processed_results["test_results"].append(test_info)

        # Write the processed results to results.json, overwriting the Jest output
        with open(results_file, "w") as f:
            json.dump(processed_results, f, indent=2)
            
        return processed_results

    except Exception as e:
        error_result = {
            "error": f"Error processing submission: {str(e)}",
            "passed": 0,
            "failed": 0,
            "total": 0
        }
        
        # Try to write the error to results.json if possible
        try:
            results_dir = Path("submissions") / f"submission_{submission_id}" / "results"
            if not results_dir.exists():
                results_dir.mkdir(parents=True, exist_ok=True)
            with open(results_dir / "results.json", "w") as f:
                json.dump(error_result, f, indent=2)
        except Exception:
            # If we can't even write the error, just return it
            pass
            
        return error_result

# Example usage
if __name__ == "__main__":
    sample_code = """
    console.log("Hello, World!");
    """
    # To run with only visible test cases
    result_visible = process_code_submission(sample_code, "js-print-hello", hidden=False)
    
    # To run with both visible and hidden test cases
    result_all = process_code_submission(sample_code, "js-print-hello", hidden=True)