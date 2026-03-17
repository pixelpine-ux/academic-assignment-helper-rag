from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User
from app.core.dependencies import get_current_user
from app.services.vector_search_service import search_chunks
from app.services.llm_service import generate_answer
from app.schemas.query import QueryRequest, QueryResponse

router = APIRouter(prefix="/query", tags=["query"])


@router.post("/", response_model=QueryResponse)
def rag_query(
    body: QueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not body.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    chunks = search_chunks(body.question, current_user.id, db)

    if not chunks:
        raise HTTPException(
            status_code=404,
            detail="No relevant documents found. Upload documents before querying."
        )

    result = generate_answer(body.question, chunks)

    return QueryResponse(question=body.question, **result)
