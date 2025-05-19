from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from db import get_session
from sonar import ask_sonar
from models import Exam, Course
from datetime import datetime

router = APIRouter()

@router.post("/course/")
def add_course(
    progress_id: int,
    name: str,
    current_grade: float,
    target_grade: float,
    free_hours_per_day: float,
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
        return {"error": "Course not found"}

    if current_grade is not None:
        course.current_grade = current_grade
    if target_grade is not None:
        course.target_grade = target_grade
    if free_hours_per_day is not None:
        course.free_hours_per_day = free_hours_per_day

    session.add(course)
    session.commit()
    return course


@router.get("/course/{progress_id}")
def get_courses_for_progress(progress_id: int, session: Session = Depends(get_session)):
    return session.exec(select(Course).where(Course.progress_id == progress_id)).all()


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
