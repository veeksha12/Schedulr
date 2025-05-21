from pydantic import BaseModel
from typing import Optional
from datetime import date

class ExamBase(BaseModel):
    name: str
    date: date
    marks_obtained: Optional[float]
    max_marks: Optional[float]
    weightage: float

class ExamCreate(ExamBase):
    pass

class ExamUpdate(ExamBase):
    pass

class ExamInDB(ExamBase):
    id: int
    course_id: int

    class Config:
        orm_mode = True
