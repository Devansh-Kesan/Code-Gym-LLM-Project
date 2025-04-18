"""Test module for JavaScript code submissions using Docker."""

import sys
from pathlib import Path

# Import the process_code_submission function for JavaScript
# Adjust the import path if necessary to match your project structure
sys.path.append(str(Path(__file__).resolve().parent.parent))
from js_submission_processor import process_code_submission


def test_with_real_docker_js(
    problem_id: str,
    user_code: str,
    *,
    hidden: bool,
) -> dict | None:
    """Test process_code_submission function with real Docker container for JS."""
    try:
        return process_code_submission(
            user_code=user_code,
            problem_id=problem_id,
            hidden=hidden,
        )
    except RuntimeError as exc:
        error_message = f"Error testing function: {exc!s}"
        raise RuntimeError(error_message) from exc


if __name__ == "__main__":
    problem_id = "js-switch-day"
    user_code = """
const readline = require("readline");

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

function getDay(num) {
  switch (Number(num)) {
    case 1: console.log("Monday1"); break;
    case 2: console.log("Tuesday1"); break;
    case 3: console.log("Wednesday1"); break;
    case 4: console.log("Thursday1"); break;
    case 5: console.log("Friday1"); break;
    case 6: console.log("Saturday1"); break;
    case 7: console.log("Sunday1"); break;
    default: console.log("Invalid");
  }
}

rl.question("", (input) => {
  getDay(input);
  rl.close();
});
"""
    results = test_with_real_docker_js(
        problem_id=problem_id,
        user_code=user_code,
        hidden=True,
    )
