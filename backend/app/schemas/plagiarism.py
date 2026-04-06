from pydantic import BaseModel
from typing import Optional


class HashCheckResult(BaseModel):
    is_duplicate: bool
    matched_document_id: Optional[int] = None


class VectorCheckResult(BaseModel):
    is_flagged: bool
    similarity_score: float
    matched_document_id: Optional[int] = None


class PlagiarismResult(BaseModel):
    document_id: int
    filename: str
    hash_check: HashCheckResult
    vector_check: VectorCheckResult
