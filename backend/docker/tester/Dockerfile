# Dockerfile for the code-gym-tester
FROM python:3.12-slim

WORKDIR /app

# Install pytest and other dependencies
RUN pip install pytest pytest-json-report

# Copy the test runner script
COPY test_runner.py /app/

# Entry point will be your test runner
ENTRYPOINT ["python", "test_runner.py"]