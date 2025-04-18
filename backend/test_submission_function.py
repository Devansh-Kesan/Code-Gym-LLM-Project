"""Test submission function with Docker container."""

import sys
from pathlib import Path
from typing import Any

# Import the process_code_submission function
# Adjust the import path if necessary to match your project structure
sys.path.append(str(Path(__file__).resolve().parent.parent))
from submission_processor import process_code_submission


def test_with_real_docker(
    problem_id: str,
    user_code: str,
    *,  # Force keyword arguments after this point
    hidden: bool,
) -> dict[str, Any] | None:
    """Test the process_code_submission function with a real Docker container.

    Args:
        problem_id: The ID of the problem being tested
        user_code: The user's code to be tested
        hidden: Whether to include hidden test cases

    Returns:
        Dictionary with test results or None if an error occurred

    """
    try:
        # Call the actual function
        return process_code_submission(
            user_code=user_code,
            problem_id=problem_id,
            hidden=hidden,
        )

    except (ValueError, RuntimeError) as exc:
        return {
            "error": f"Error testing function: {exc!s}",
            "passed": 0,
            "failed": 0,
            "total": 0,
        }


if __name__ == "__main__":
    problem_id = "sum-of-list"
    user_code = """
def sum_of_list(lst):
    # Simple implementation using sum() function
    # while(1):
        # continue
    print(1)
    return lst[0]

if __name__ == "__main__":
    nums = list(map(int, input().split()))
    print(sum_of_list(nums))
"""
    results = test_with_real_docker(
        problem_id=problem_id,
        user_code=user_code,
        hidden=True,
    )
