"""TestRunner."""

import glob
import json
import os
import shutil
import sys

import pytest


def run_tests() -> bool:
    """Run all test cases against the user solution and generate a results report."""
    results = {
        "passed": 0,
        "failed": 0,
        "total": 0,
        "test_results": [],
    }

    # Get all test files
    test_files = glob.glob("/tests/test_*.py")
    results["total"] = len(test_files)

    # Create a temporary directory for pytest
    os.makedirs("/app/pytest_temp", exist_ok=True)

    for test_file in test_files:
        test_name = os.path.basename(test_file)
        test_id = test_name.replace("test_", "").replace(".py", "")
        is_hidden = "hidden" in test_id

        # Run pytest for this test file
        pytest_args = [
            "-xvs",
            test_file,
            "--json-report",
            "--json-report-file=/app/pytest_temp/report.json",
        ]

        pytest_result = pytest.main(pytest_args)

        # Determine if test passed
        passed = pytest_result == 0

        # Get error message if test failed
        error_message = ""
        if not passed:
            try:
                with open("/app/pytest_temp/report.json") as f:
                    report = json.load(f)

                for test_result in report.get("tests", []):
                    if test_result.get("outcome") == "failed":
                        error_message = test_result.get("call", {}).get("longrepr", "")
                        break
            except Exception as e:
                error_message = f"Error reading test results: {e!s}"

        # Update results
        if passed:
            results["passed"] += 1
        else:
            results["failed"] += 1

        # For hidden test cases, don't reveal the exact error
        if is_hidden and not passed:
            error_message = "Hidden test case failed"

        results["test_results"].append({
            "test_name": test_name,
            "passed": passed,
            "is_hidden": is_hidden,
            "error": error_message if not passed else "",
        })

    # Write results to the mounted volume
    with open("/results/results.json", "w") as f:
        json.dump(results, f, indent=2)

    # Clean up
    shutil.rmtree("/app/pytest_temp", ignore_errors=True)

    # Exit with status code based on test results
    return results["failed"] == 0

if __name__ == "__main__":
    # Add code directory to path so we can import the solution
    sys.path.append("/code")

    # Run tests and exit with appropriate status code
    success = run_tests()
    sys.exit(0 if success else 1)
