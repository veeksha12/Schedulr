# path/planner.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..db import get_db          # your SessionLocal provider
from ..auth import get_current_user  # returns User model
from ..crud import planner as crud
from ..schemas.planner import PlannerCreate, PlannerUpdate, PlannerOut

router = APIRouter(prefix="/planner", tags=["Planner"])

@router.get("/", response_model=list[PlannerOut])
def list_planners(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return crud.get_planners(db, user.id)

@router.post("/", response_model=PlannerOut, status_code=status.HTTP_201_CREATED)
def create_planner(data: PlannerCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return crud.create_planner(db, user.id, data)

@router.get("/{planner_id}", response_model=PlannerOut)
def get_planner(planner_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    planner = crud.get_planner(db, planner_id, user.id)
    if not planner:
        raise HTTPException(404, "Planner not found")
    return planner

@router.patch("/{planner_id}", response_model=PlannerOut)
def update_planner(planner_id: int, data: PlannerUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    planner = crud.get_planner(db, planner_id, user.id)
    if not planner:
        raise HTTPException(404, "Planner not found")
    return crud.update_planner(db, planner, data)

@router.delete("/{planner_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_planner(planner_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    planner = crud.get_planner(db, planner_id, user.id)
    if not planner:
        raise HTTPException(404, "Planner not found")
    crud.delete_planner(db, planner)
