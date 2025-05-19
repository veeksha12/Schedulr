from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from passlib.hash import bcrypt
from jose import jwt
from .models import User
from db import get_session
import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

router = APIRouter()

@router.post("/register")
def register(username: str, password: str, session: Session = Depends(get_session)):
    if session.exec(select(User).where(User.username == username)).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    user = User(username=username, password_hash=bcrypt.hash(password))
    session.add(user)
    session.commit()
    return {"message": "Registered successfully"}

@router.post("/login")
def login(username: str, password: str, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == username)).first()
    if not user or not bcrypt.verify(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = jwt.encode({"user_id": user.id}, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token}
