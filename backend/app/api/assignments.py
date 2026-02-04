from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from database import get_db
from models import Assignment, User
from app.schemas.assignment import AssignmentCreate, AssignmentUpdate, Assignment as AssignmentSchema, ErrorResponse

router = APIRouter(prefix="/assignments", tags=["assignments"])

def create_error_response(error: str, detail: str, status_code: int):
    """Standardized error response helper"""
    raise HTTPException(
        status_code=status_code,
        detail={"error": error, "detail": detail, "status_code": status_code}
    )

@router.post("/", response_model=AssignmentSchema, responses={400: {"model": ErrorResponse}})
def create_assignment(assignment: AssignmentCreate, db: Session = Depends(get_db)):
    # Validate user exists
    user = db.query(User).filter(User.id == assignment.created_by).first()
    if not user:
        create_error_response("Validation Error", "User not found", 400)
    
    try:
        db_assignment = Assignment(**assignment.dict())
        db.add(db_assignment)
        db.commit()
        db.refresh(db_assignment)
        return db_assignment
    except Exception as e:
        db.rollback()
        create_error_response("Database Error", "Failed to create assignment", 500)

@router.get("/", response_model=List[AssignmentSchema])
def get_assignments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    status: Optional[str] = Query(None, regex="^(draft|published|submitted|graded)$"),
    due_before: Optional[datetime] = Query(None, description="Filter assignments due before this date"),
    db: Session = Depends(get_db)
):
    query = db.query(Assignment)
    
    if user_id:
        query = query.filter(Assignment.created_by == user_id)
    if status:
        query = query.filter(Assignment.status == status)
    if due_before:
        query = query.filter(Assignment.due_date <= due_before)
    
    assignments = query.offset(skip).limit(limit).all()
    return assignments

@router.get("/{assignment_id}", response_model=AssignmentSchema, responses={404: {"model": ErrorResponse}})
def get_assignment(assignment_id: int, db: Session = Depends(get_db)):
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        create_error_response("Not Found", "Assignment not found", 404)
    return assignment

@router.put("/{assignment_id}", response_model=AssignmentSchema, responses={404: {"model": ErrorResponse}, 400: {"model": ErrorResponse}})
def update_assignment(assignment_id: int, assignment_update: AssignmentUpdate, db: Session = Depends(get_db)):
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        create_error_response("Not Found", "Assignment not found", 404)
    
    try:
        update_data = assignment_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(assignment, field, value)
        
        db.commit()
        db.refresh(assignment)
        return assignment
    except Exception as e:
        db.rollback()
        create_error_response("Database Error", "Failed to update assignment", 500)

@router.delete("/{assignment_id}", responses={404: {"model": ErrorResponse}})
def delete_assignment(assignment_id: int, db: Session = Depends(get_db)):
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        create_error_response("Not Found", "Assignment not found", 404)
    
    try:
        db.delete(assignment)
        db.commit()
        return {"message": "Assignment deleted successfully"}
    except Exception as e:
        db.rollback()
        create_error_response("Database Error", "Failed to delete assignment", 500)