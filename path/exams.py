from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List, Optional
from datetime import date

# Assuming these modules exist:
import crud.exam as exam_crud
import schemas.exam as exam_schemas

from db import get_session  # your SQLModel session dependency
from models import Exam      # your SQLModel Exam model

router = APIRouter(prefix="/exams", tags=["exams"])

# --- Using crud + schemas style ---

@router.get("/progress/{progress_id}/courses/{course_id}/exams", response_model=List[exam_schemas.ExamInDB])
def read_exams(progress_id: int, course_id: int, db: Session = Depends(get_session)):
    # Optionally validate user progress access here
    return exam_crud.get_exams_for_course(db, course_id)

@router.post("/progress/{progress_id}/courses/{course_id}/exams", response_model=exam_schemas.ExamInDB)
def create_exam(progress_id: int, course_id: int, exam: exam_schemas.ExamCreate, db: Session = Depends(get_session)):
    # Optionally validate user progress access here
    return exam_crud.create_exam(db, course_id, exam)

@router.put("/{exam_id}", response_model=exam_schemas.ExamInDB)
def update_exam(exam_id: int, exam_update: exam_schemas.ExamUpdate, db: Session = Depends(get_session)):
    updated = exam_crud.update_exam(db, exam_id, exam_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Exam not found")
    return updated

@router.delete("/{exam_id}")
def delete_exam(exam_id: int, db: Session = Depends(get_session)):
    exam_crud.delete_exam(db, exam_id)
    return {"detail": "Exam deleted successfully"}

# --- Direct session access style (SQLModel) ---

@router.post("/exam/")
def add_exam(
    course_id: int,
    name: str,
    date: date,
    weightage: float,
    score: Optional[float] = None,
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
        raise HTTPException(status_code=404, detail="Exam not found")

    exam.score = score
    session.add(exam)
    session.commit()
    session.refresh(exam)
    return exam

@router.get("/exam/{course_id}")
def get_exams_for_course(course_id: int, session: Session = Depends(get_session)):
    exams = session.exec(select(Exam).where(Exam.course_id == course_id)).all()
    return exams
