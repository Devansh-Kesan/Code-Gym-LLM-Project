
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

def test_hidden_0():
    signal.alarm(5)
    captured_output = io.StringIO()
    sys.stdout = captured_output
    sys.stdin = io.StringIO('''0''')
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
    expected = '''Zero'''.strip()
    if output != expected:
        error_info = {
            "error_type": "AssertionError",
            "expected": expected,
            "actual": output
        }
        pytest.fail(json.dumps(error_info))
