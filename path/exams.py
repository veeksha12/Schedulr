from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from models import Exam
from db import get_session
from datetime import date

router = APIRouter()

@router.post("/exam/")
def add_exam(
    course_id: int,
    name: str,
    date: date,
    weightage: float,
    score: float = None,
    session: Session = Depends(get_session)
):
    exam = Exam(
        course_id=course_id,
        name=name,
        date=date,
        weightage=weightage,
        score=score
    )
    session.add(exam)
    session.commit()
    session.refresh(exam)
    return exam


@router.put("/exam/{exam_id}")
def update_exam_score(exam_id: int, score: float, session: Session = Depends(get_session)):
    exam = session.get(Exam, exam_id)
    if not exam:
        return {"error": "Exam not found"}

    exam.score = score
    session.add(exam)
    session.commit()
    return exam


@router.get("/exam/{course_id}")
def get_exams_for_course(course_id: int, session: Session = Depends(get_session)):
    return session.exec(select(Exam).where(Exam.course_id == course_id)).all()
