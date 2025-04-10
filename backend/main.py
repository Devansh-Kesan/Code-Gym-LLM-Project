# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

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
print("QQD",questions_data)


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
