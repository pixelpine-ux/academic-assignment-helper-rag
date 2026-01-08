from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Assignment
from app.schemas.assignment import AssignmentCreate, AssignmentUpdate, Assignment as AssignmentSchema

router = APIRouter(prefix="/assignments", tags=["assignments"])

@router.post("/", response_model=AssignmentSchema)
def create_assignment(assignment: AssignmentCreate, db: Session = Depends(get_db)):
    db_assignment = Assignment(**assignment.dict())
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    return db_assignment

@router.get("/", response_model=List[AssignmentSchema])
def get_assignments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    assignments = db.query(Assignment).offset(skip).limit(limit).all()
    return assignments

@router.get("/{assignment_id}", response_model=AssignmentSchema)
def get_assignment(assignment_id: int, db: Session = Depends(get_db)):
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return assignment

@router.put("/{assignment_id}", response_model=AssignmentSchema)
def update_assignment(assignment_id: int, assignment_update: AssignmentUpdate, db: Session = Depends(get_db)):
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    update_data = assignment_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(assignment, field, value)
    
    db.commit()
    db.refresh(assignment)
    return assignment

@router.delete("/{assignment_id}")
def delete_assignment(assignment_id: int, db: Session = Depends(get_db)):
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    db.delete(assignment)
    db.commit()
    return {"message": "Assignment deleted successfully"}