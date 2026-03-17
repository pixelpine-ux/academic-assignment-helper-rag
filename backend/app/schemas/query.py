from pydantic import BaseModel
from typing import List


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    question: str
    answer: str
    source_document_ids: List[int]
    chunks_used: int
