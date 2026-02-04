from pydantic import BaseModel, validator, Field
from datetime import datetime
from typing import Optional, List

class AssignmentBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    due_date: Optional[datetime] = None
    
    @validator('due_date')
    def due_date_must_be_future(cls, v):
        if v and v <= datetime.now():
            raise ValueError('Due date must be in the future')
        return v

class AssignmentCreate(AssignmentBase):
    created_by: int = Field(..., gt=0)

class AssignmentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    due_date: Optional[datetime] = None
    status: Optional[str] = Field(None, regex='^(draft|published|submitted|graded)$')
    
    @validator('due_date')
    def due_date_must_be_future(cls, v):
        if v and v <= datetime.now():
            raise ValueError('Due date must be in the future')
        return v

class ErrorResponse(BaseModel):
    error: str
    detail: str
    status_code: int

class Assignment(AssignmentBase):
    id: int
    status: str
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True