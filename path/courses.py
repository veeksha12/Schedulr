from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from db import get_session
from sonar import ask_sonar
from models import Exam, Course
from datetime import datetime
from typing import List

router = APIRouter()

def calculate_course_grade(session: Session, course_id: int) -> float:
    exams = session.exec(select(Exam).where(Exam.course_id == course_id)).all()
    if not exams:
        return 0.0
    total_weightage = sum(e.weightage for e in exams if e.weightage is not None)
    if total_weightage == 0:
        return 0.0

    weighted_sum = 0.0
    for e in exams:
        if e.score is not None and e.weightage is not None and e.max_marks is not None:
            weighted_sum += (e.score / e.max_marks) * e.weightage
    # Normalize to percentage scale (0-100)
    return round((weighted_sum / total_weightage) * 100, 2)


@router.post("/course/")
def add_course(
    progress_id: int,
    name: str,
    current_grade: float = 0.0,
    target_grade: float = 100.0,
    free_hours_per_day: float = 0.0,
    session: Session = Depends(get_session)
):
    course = Course(
        progress_id=progress_id,
        name=name,
        current_grade=current_grade,
        target_grade=target_grade,
        free_hours_per_day=free_hours_per_day
    )
    session.add(course)
    session.commit()
    session.refresh(course)
    return course


@router.put("/course/{course_id}")
def update_course(
    course_id: int,
    current_grade: float = None,
    target_grade: float = None,
    free_hours_per_day: float = None,
    session: Session = Depends(get_session)
):
    course = session.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    if current_grade is not None:
        course.current_grade = current_grade
    if target_grade is not None:
        course.target_grade = target_grade
    if free_hours_per_day is not None:
        course.free_hours_per_day = free_hours_per_day

    session.add(course)
    session.commit()
    return course


@router.get("/course/{progress_id}", response_model=List[Course])
def get_courses_for_progress(progress_id: int, session: Session = Depends(get_session)):
    courses = session.exec(select(Course).where(Course.progress_id == progress_id)).all()
    if not courses:
        raise HTTPException(status_code=404, detail="No courses found for this progress_id")

    # Inject dynamically calculated current_grade based on exams
    for course in courses:
        course.current_grade = calculate_course_grade(session, course.id)
    return courses


@router.post("/course/{course_id}/autograde")
def auto_update_grade(course_id: int, session: Session = Depends(get_session)):
    course = session.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    exams = session.exec(select(Exam).where(Exam.course_id == course_id)).all()
    if not exams:
        raise HTTPException(status_code=400, detail="No exams found for this course")

    prompt = f"""You're an academic assistant. A student has scored the following in a course:\n"""
    for exam in exams:
        if exam.score is not None:
            prompt += f"- {exam.name}: {exam.score} marks, weightage: {exam.weightage}%\n"

    prompt += (
        "\nEstimate the current grade of the student in this course on a 10-point scale. "
    )

    response = ask_sonar(prompt)

    try:
        grade = float(response.strip().split()[0])
        course.current_grade = round(grade, 2)
        session.add(course)
        session.commit()
        return {"updated_grade": course.current_grade}
    except Exception:
        raise HTTPException(status_code=500, detail=f"Sonar response error: {response}")
