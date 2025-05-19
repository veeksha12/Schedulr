from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from db import get_session
from models import Progress, Course, Exam

router = APIRouter()


@router.post("/progress/")
def create_progress(title: str, user_id: int, session: Session = Depends(get_session)):
    progress = Progress(title=title, user_id=user_id)
    session.add(progress)
    session.commit()
    session.refresh(progress)
    return progress


@router.get("/progress/{user_id}")
def get_all_progress(user_id: int, session: Session = Depends(get_session)):
    return session.exec(select(Progress).where(Progress.user_id == user_id)).all()
