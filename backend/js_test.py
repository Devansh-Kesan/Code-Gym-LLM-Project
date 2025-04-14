# js_test.py
import os
import sys
from pathlib import Path

# Import the process_code_submission function for JavaScript
# Adjust the import path if necessary to match your project structure
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from js_submission_processor import process_code_submission

def test_with_real_docker_js(problem_id, user_code, hidden):
    """
    Test the process_code_submission function with a real Docker container for JavaScript.
    """
    print("Testing process_code_submission function with Docker for JavaScript...")
    
    try:
        # Call the actual function
        results = process_code_submission(user_code, problem_id,hidden)
        
        return results
        
    except Exception as e:
        print(f"Error testing function: {str(e)}")
        return None

# Run the test
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
    case 1: console.log("Monday"); break;
    case 2: console.log("Tuesday"); break;
    case 3: console.log("Wednesday"); break;
    case 4: console.log("Thursday"); break;
    case 5: console.log("Friday"); break;
    case 6: console.log("Saturday"); break;
    case 7: console.log("Sunday"); break;
    default: console.log("Invalid");
  }
}

rl.question("", (input) => {
  getDay(input);
  rl.close();
});


"""
    results = test_with_real_docker_js(problem_id, user_code, True)
    print("Test Results:", results)