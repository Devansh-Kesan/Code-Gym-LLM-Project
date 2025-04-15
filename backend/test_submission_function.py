# test_submission_function.py
import os
import sys
from pathlib import Path

# Import the process_code_submission function
# Adjust the import path if necessary to match your project structure
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from submission_processor import process_code_submission

def test_with_real_docker(problem_id, user_code, hidden):
    """
    Test the process_code_submission function with a real Docker container.
    """
    print("Testing process_code_submission function with Docker...")
    
    try:
        # Call the actual function
        results = process_code_submission(user_code, problem_id, hidden)
        
        return results
        
    except Exception as e:
        print(f"Error testing function: {str(e)}")
        return None

# Run the test
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
    results = test_with_real_docker(problem_id,user_code,True)
    