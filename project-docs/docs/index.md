# Code GYM - Code LLM

**Code GYM - Code LLM** is a hands-on coding platform powered by Large Language Models (LLMs) designed to help learners practice programming and receive intelligent assistance while solving real-world problems. It blends structured course content with dynamic AI features to enhance the coding learning experience.

## Features

- 🌟 **Interactive Code Editor** with real-time feedback  
- 🤖 **LLM-powered Assistance**:  
  &nbsp;&nbsp;&nbsp;&nbsp;- Progressive Hints System  
  &nbsp;&nbsp;&nbsp;&nbsp;- Error Explanation  
  &nbsp;&nbsp;&nbsp;&nbsp;- Test Case Generation  
  &nbsp;&nbsp;&nbsp;&nbsp;- Code Review Assistant  
  &nbsp;&nbsp;&nbsp;&nbsp;- Conceptual Scaffolding  
- 📚 **Topic-Based Courses**:  
  &nbsp;&nbsp;&nbsp;&nbsp;- Python and JavaScript programming  
  &nbsp;&nbsp;&nbsp;&nbsp;- Each topic contains structured problems with difficulty levels  
- ⚙️ **Auto-Graded Code Execution** via Docker sandboxing  
- 📄 **Fully YAML-Driven Content** — no databases required  

## Tech Stack

- **LLM Runner**: Ollama  
- **LLM Model**: `qwen2.5:7b` (hosted locally via Ollama)  
- **Backend Framework**: FastAPI  
- **Frontend Framework**: HTML, CSS, JS  
- **Course Config**: Single `config.yaml` file (contains all course and question metadata)  
- **Orchestration & Logging**: Prefect / DBOS + MLflow  
- **Code Execution**: Docker-based secure execution for user-submitted code  

## Course Content Structure

- Each course (Python, JS) includes 5 topics  
- Every topic contains 6 problems:  
  &nbsp;&nbsp;&nbsp;&nbsp;- Metadata: ID, title, difficulty, etc.  
  &nbsp;&nbsp;&nbsp;&nbsp;- Starter code & solution  
  &nbsp;&nbsp;&nbsp;&nbsp;- Public and hidden test cases  
- All content is defined in YAML for easy authoring and versioning  

---

Start coding, learn smarter, and level up your skills with **Code GYM - Code LLM**.
