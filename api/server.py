"""
server.py
A small FastAPI server that exposes your AI pipeline as an HTTP endpoint.
Person 3 (Node.js) calls this instead of importing pipeline.py directly.

Run with: uvicorn server:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from pipeline import run_career_pipeline

app = FastAPI()

# Allow Node.js backend to call this server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Request shape ----------

class Student(BaseModel):
    name: Optional[str] = "Student"
    education: Optional[str] = "Not specified"
    age: Optional[int] = None


class QuizAnswers(BaseModel):
    subjects: List[str]
    interests: List[str]
    strengths: List[str]
    work_style: Optional[str] = "Not specified"
    goal: Optional[str] = "Not specified"


class RecommendRequest(BaseModel):
    student: Student
    quiz_answers: QuizAnswers


# ---------- Endpoint ----------

@app.post("/recommend")
def recommend(request: RecommendRequest):
    student = request.student.dict()
    quiz_answers = request.quiz_answers.dict()
    result = run_career_pipeline(student, quiz_answers)
    return result


@app.get("/health")
def health():
    return {"status": "ok", "message": "AI engine is running"}