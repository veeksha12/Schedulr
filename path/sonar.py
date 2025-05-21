import os
import httpx
from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy.orm import Session
from models import Exam, Course

router = APIRouter()

class GradeHelpRequest(BaseModel):
    current_grade: float
    target_grade: float
    hours_per_day: float
    weeks_remaining: int

@router.post("/ai/grade-help")
async def grade_difficulty_feedback(request: GradeHelpRequest):
    api_key = os.getenv("SONAR_API_KEY")
    if not api_key:
        return {"error": "Missing API key."}

    prompt = (
        f"A student currently has a grade of {request.current_grade}%. "
        f"They want to achieve {request.target_grade}% in {request.weeks_remaining} weeks, "
        f"studying {request.hours_per_day} hours per day.\n\n"
        "Rate how difficult this goal is on a scale from 1 to 10, and give suggestions to adjust time commitment or strategies. "
        "Be realistic, constructive, and student-friendly."
    )

    url = "https://api.perplexity.ai/chat/completions"
    payload = {
        "model": "sonar-small-chat",
        "messages": [
            {"role": "system", "content": "You are a helpful academic advisor."},
            {"role": "user", "content": prompt}
        ]
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        return {"error": f"Sonar API error: {response.text}"}

    result = response.json()
    return {"response": result["choices"][0]["message"]["content"]}


class ChatRequest(BaseModel):
    query: str

@router.post("/ai/chat")
async def ask_chatbot(request: ChatRequest):
    api_key = os.getenv("SONAR_API_KEY")
    if not api_key:
        return {"error": "Missing SONAR_API_KEY"}

    prompt = request.query.strip()

    url = "https://api.perplexity.ai/chat/completions"
    payload = {
        "model": "sonar-small-chat",
        "messages": [
            {"role": "system", "content": "You are a helpful academic assistant that gives study tips and productivity suggestions."},
            {"role": "user", "content": prompt}
        ]
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        return {"error": f"Sonar API error: {response.text}"}

    result = response.json()
    return {"response": result["choices"][0]["message"]["content"]}


def calculate_course_grade(db: Session, course_id: int) -> float:
    exams = db.query(Exam).filter(Exam.course_id == course_id).all()
    if not exams:
        return 0.0
    total_weightage = sum(e.weightage for e in exams)
    if total_weightage == 0:
        return 0.0

    weighted_sum = 0.0
    for e in exams:
        if e.marks_obtained is not None and e.max_marks is not None and e.max_marks != 0:
            weighted_sum += (e.marks_obtained / e.max_marks) * e.weightage
    # Return weighted grade out of 100
    return (weighted_sum / total_weightage) * 100
