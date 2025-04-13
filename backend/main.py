# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from services.llm_hint import generate_progressive_hints
from services.llm_error import generate_error_explanation
from services.llm_testcases import generate_test_cases
from services.llm_review import generate_code_review
from services.pydantic_models import LLMRequest
from test_submission_function import test_with_real_docker

import yaml
import os

app = FastAPI()

# Enable CORS so frontend can call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

courses_data = {}
questions_data = {}

def load_config(path="config.yaml"):
    global courses_data, questions_data

    with open(path, "r") as file:
        config = yaml.safe_load(file)

    for course in config.get("courses", []):
        # print("CC",course)
        course_id = course["id"]
        courses_data[course_id] = course

        # Flatten and collect question data
        for topic in course.get("topics", []):
            for question in topic.get("questions", []):
                # print("QQ",question)
                qid = question["id"]
                questions_data[qid] = question

# Load everything from config.yaml
load_config()
# print("CCD",courses_data)

i=0
for k,v in questions_data.items():
    i+=1
    # print(f"K : {k} and V : {v}")
    # i+=1
    # if (i==1):
    #     break
print(i)


@app.get("/debug")
def debug():
    return questions_data

@app.get("/courses")
def get_courses():
    return [j for j in courses_data.values()]

@app.get("/courses/{course_id}")
def get_course(course_id: str):
    course = courses_data.get(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@app.get("/courses/{course_id}/topics")
def get_topics(course_id: str):
    course = courses_data.get(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course.get("topics", {})

@app.get("/courses/{course_id}/topics/{topic_id}")
def get_topic(course_id: str, topic_id: str):
    course = courses_data.get(course_id)
    topic = next((t for t in course.get("topics", []) if t["topic_id"] == topic_id), None)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic

@app.get("/courses/{course_id}/topics/{topic_id}/questions/{question_id}")
def get_question(question_id: str):
    question = questions_data.get(question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question

@app.post("/llm/hint")
def get_hint(request: LLMRequest):
    hints = generate_progressive_hints(
        question_title=request.title,
        question_description=request.description,
        user_code=request.code
    )
    return {"hints": hints}

@app.post("/llm/explain-error")
def get_error_explanation(request: LLMRequest):
    explanations = generate_error_explanation(
        question_title=request.title,
        question_description=request.description,
        user_code=request.code
    )
    return {"explanations": explanations}

@app.post("/llm/test-cases")
def get_test_cases(request: LLMRequest):
    test_cases = generate_test_cases(
        question_title=request.title,
        question_description=request.description,
        user_code=request.code
    )
    return {"test_cases": test_cases}

@app.post("/llm/code-review")
def get_code_review(request: LLMRequest):
    review = generate_code_review(
        question_title=request.title,
        question_description=request.description,
        user_code=request.code
    )
    return {"review": review}

class RunCodeRequest(BaseModel):
    code: str
    question_id: str

@app.post("/run-code")
def run_user_code(request:RunCodeRequest):
    code=request.code
    question_id=request.question_id
    result = test_with_real_docker(question_id,code,False)

    return result

@app.post("/run-code-all")
def run_user_code(request:RunCodeRequest):
    code=request.code
    question_id=request.question_id
    
    result = test_with_real_docker(question_id,code,True)

    return result




    