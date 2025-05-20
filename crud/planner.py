from sqlalchemy.orm import Session
from .. import models
from ..schemas.planner import PlannerCreate, PlannerUpdate

def get_planners(db: Session, user_id: int):
    return db.query(models.Planner).filter(models.Planner.user_id == user_id).all()

def get_planner(db: Session, planner_id: int, user_id: int):
    return (
        db.query(models.Planner)
        .filter(models.Planner.id == planner_id, models.Planner.user_id == user_id)
        .first()
    )

def create_planner(db: Session, user_id: int, data: PlannerCreate):
    obj = models.Planner(user_id=user_id, **data.dict(exclude_unset=True))
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def update_planner(db: Session, db_obj: models.Planner, data: PlannerUpdate):
    for k, v in data.dict(exclude_unset=True).items():
        setattr(db_obj, k, v)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete_planner(db: Session, db_obj: models.Planner):
    db.delete(db_obj)
    db.commit()
