# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

# Enable CORS so frontend can call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sample Data
courses_data = {
    "python-basics": {
        "title": "Python Basics",
        "description": "Learn the fundamentals of Python.",
        "language": "Python",
        "topics": {
            "variables-data-types": {
                "title": "Variables and Data Types",
                "levels": {
                    "beginner": {
                        "questions": ["hello-world"]
                    }
                }
            }
        }
    },
    "cpp-basics": {
        "title": "C++ Basics",
        "description": "Learn C++ from scratch.",
        "language": "C++",
        "topics": {}
    }
}

questions_data = {
    "hello-world": {
        "title": "Hello World!",
        "description": "Write a program that prints Hello, World!",
        "starter_code": "print(\"Hello, World!\")"
    }
}

# API Routes
@app.get("/info")
def get_info():
    return {"app": "LearnCode API", "version": "1.0"}

@app.get("/languages")
def get_languages():
    return list({c['language'] for c in courses_data.values()})

@app.get("/courses")
def get_courses():
    return [{"id": cid, **data} for cid, data in courses_data.items()]

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
    topic = course.get("topics", {}).get(topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic

@app.get("/courses/{course_id}/topics/{topic_id}/levels/{level}")
def get_questions(course_id: str, topic_id: str, level: str):
    topic = courses_data.get(course_id, {}).get("topics", {}).get(topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic.get("levels", {}).get(level, {}).get("questions", [])

@app.get("/questions/{question_id}")
def get_question(question_id: str):
    question = questions_data.get(question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question
