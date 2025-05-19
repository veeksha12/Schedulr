from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import date
from pydantic import BaseModel
from typing import List

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    password_hash: str

    progresses: List["Progress"] = Relationship(back_populates="user")


class Progress(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str  # degree/year/task
    user_id: int = Field(foreign_key="user.id")

    user: User = Relationship(back_populates="progresses")
    courses: List["Course"] = Relationship(back_populates="progress")


class Course(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    current_grade: float
    target_grade: float
    free_hours_per_day: float
    progress_id: int = Field(foreign_key="progress.id")

    progress: Progress = Relationship(back_populates="courses")
    exams: List["Exam"] = Relationship(back_populates="course")


class Exam(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    date: date
    weightage: float
    score: Optional[float] = None
    course_id: int = Field(foreign_key="course.id")

    course: Course = Relationship(back_populates="exams")

class Task(BaseModel):
    id: int
    date: str  # YYYY-MM-DD
    description: str
    completed: bool
