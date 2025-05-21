from sqlalchemy.orm import Session
from models import Exam
from schemas.exam import ExamCreate, ExamUpdate
from typing import List

def get_exams_for_course(db: Session, course_id: int) -> List[Exam]:
    return db.query(Exam).filter(Exam.course_id == course_id).all()

def create_exam(db: Session, course_id: int, exam: ExamCreate) -> Exam:
    db_exam = Exam(course_id=course_id, **exam.dict())
    db.add(db_exam)
    db.commit()
    db.refresh(db_exam)
    return db_exam

def update_exam(db: Session, exam_id: int, exam_update: ExamUpdate) -> Exam:
    db_exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not db_exam:
        return None
    for key, value in exam_update.dict().items():
        setattr(db_exam, key, value)
    db.commit()
    db.refresh(db_exam)
    return db_exam

def delete_exam(db: Session, exam_id: int):
    db_exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if db_exam:
        db.delete(db_exam)
        db.commit()
