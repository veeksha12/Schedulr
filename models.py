from typing import Optional, List
from datetime import date
from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Relationship

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    password_hash: str

    progresses: List["Progress"] = Relationship(back_populates="user")
    planners: List["Planner"] = Relationship(back_populates="user")

class Planner(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    name: str
    start_date: Optional[date] = Field(default_factory=date.today)
    end_date: Optional[date] = None

    user: User = Relationship(back_populates="planners")
    courses: List["Course"] = Relationship(back_populates="planner")
    tasks: List["Task"] = Relationship(back_populates="planner")

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

    progress_id: Optional[int] = Field(default=None, foreign_key="progress.id")
    planner_id: Optional[int] = Field(default=None, foreign_key="planner.id")

    progress: Optional[Progress] = Relationship(back_populates="courses")
    planner: Optional[Planner] = Relationship(back_populates="courses")
    exams: List["Exam"] = Relationship(back_populates="course")

class Exam(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    date: date
    weightage: float
    score: Optional[float] = None
    course_id: int = Field(foreign_key="course.id")

    course: Course = Relationship(back_populates="exams")

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    date: str  # If you want, change to date type by: date: Optional[date] = None
    description: str
    completed: bool

    planner_id: Optional[int] = Field(default=None, foreign_key="planner.id")
    planner: Optional[Planner] = Relationship(back_populates="tasks")

# Optional Task BaseModel for API schema, keep if you want:
class TaskBase(BaseModel):
    id: int
    date: str  # YYYY-MM-DD
    description: str
    completed: bool
