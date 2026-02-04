from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class AssignmentBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None

class AssignmentCreate(AssignmentBase):
    created_by: int

class AssignmentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    status: Optional[str] = None

class Assignment(AssignmentBase):
    id: int
    status: str
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True