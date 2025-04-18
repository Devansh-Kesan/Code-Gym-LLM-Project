# **Functionality**

## 1. Progressive Hints System  
- Provides step-by-step hints based on the learner’s current code.  
- Hints are generated dynamically by analyzing the logic and structure of the submitted solution.  
- Helps users gradually reach the final solution without directly revealing it.  

## 2. Error Explanation  
- Explains runtime or logical errors in the user’s code.  
- The LLM identifies common mistakes and describes them in plain language.  
- Often includes suggestions or corrections to guide the user.  

## 3. Test Case Generation  
- Automatically generates additional test cases based on the problem description and user code.  
- Ensures broader coverage and edge case handling.  
- Helps learners test their code beyond the provided examples.  

## 4. Code Review Assistant  
- Reviews the submitted code and provides feedback on style, structure, and efficiency.  
- Suggests improvements while maintaining the original logic.  
- Encourages clean, readable, and optimized code practices.  

## 5. Conceptual Scaffolding  
- Offers brief explanations of relevant concepts based on user queries or stuck points.  
- Useful for bridging knowledge gaps without having to leave the platform.  
- Acts like a just-in-time tutor for coding concepts and problem-solving strategies.  

## 6. Secure Code Execution  
- Executes user-submitted code within isolated Docker containers.  
- Ensures a safe and consistent environment for running code and evaluating test cases.  
- Includes support for public and hidden test cases to validate learning outcomes.  

## 7. YAML-Driven Content Management  
- All courses, topics, and problems are defined in a single `config.yaml` file.  
- Easily editable and version-controlled without requiring a database.  
- Supports structured metadata, starter code, test cases, and solutions for each problem.

## 8. LLM Orchestration  
- All features are powered by the `qwen2.5:7b` LLM model hosted via **Ollama**.  
- Prefect/DBOS handles orchestration of requests and MLflow logs all LLM interactions.  
