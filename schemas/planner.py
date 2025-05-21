from datetime import date
from pydantic import BaseModel

class PlannerBase(BaseModel):
    name: str
    start_date: date | None = None
    end_date: date | None = None

class PlannerCreate(PlannerBase):
    pass

class PlannerUpdate(PlannerBase):
    pass

class PlannerOut(PlannerBase):
    id: int
    class Config:
        orm_mode = True
