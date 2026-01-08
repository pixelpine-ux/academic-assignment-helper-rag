from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

class DocumentBase(BaseModel):
    filename: str
    content: str
    doc_metadata: Optional[Dict[str, Any]] = None

class DocumentCreate(DocumentBase):
    assignment_id: Optional[int] = None

class Document(DocumentBase):
    id: int
    assignment_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True