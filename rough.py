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

l=[{"id": cid, **data} for cid, data in courses_data.items()]
print(l)