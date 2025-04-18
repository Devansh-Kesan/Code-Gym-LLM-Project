# Learnings & Challenges

## Challenges Faced

### 1. Latency Issues
- Some LLM-powered features (like code review and test case generation) had higher latency due to model response time.
- Required tuning the way data is passed and received from the LLM backend.

### 2. Prompt Quality & Output Control
- Crafting clear, consistent prompts for each tool (Hint Generator, Error Explainer, etc.) was tricky.
- Even small changes in wording could lead to drastically different or irrelevant outputs.

### 3. Code Execution Environment
- Ensuring secure, reproducible Docker containers for user code execution involved fine-tuning image setup and resource management.
- Also had to handle edge cases like infinite loops or excessive memory usage gracefully.

### 4. Model Evaluation
- Tried various models (e.g., `LLaMA 3.2`, `Qwen2.5:3b`) to evaluate quality, response speed, and cost-effectiveness.
- Settled on `Qwen2.5:3b` via Ollama due to its balance of reliability and performance.

## Key Learnings

### LLM Tool Isolation
- Treating each LLM-powered feature as a separate tool made debugging and prompt tuning easier.
- This modularity helped with maintenance and future scalability.

### Frontend-Backend Sync
- Building a smooth experience required tight integration between frontend events (e.g., clicking “Hint”) and backend endpoints.
- Standardized response formats helped display results consistently in the UI.

### Efficient Code Execution Pipeline
- Docker containers were optimized to quickly spin up, run code, and tear down with minimal overhead.
- Logs and test case evaluations were made transparent for better debugging and feedback.

### Improved Observability
- Added detailed logging for LLM requests, user actions, and code results using MLflow and Prefect/DBOS.
- Helped track tool usage patterns and fine-tune performance.
