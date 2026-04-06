from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User, Document
from app.core.dependencies import get_current_user
from app.services.plagiarism_service import hash_check, vector_check
from app.schemas.plagiarism import PlagiarismResult, HashCheckResult, VectorCheckResult

router = APIRouter(prefix="/documents", tags=["plagiarism"])


@router.post("/{document_id}/check-plagiarism", response_model=PlagiarismResult)
def check_plagiarism(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Check a document for plagiarism using both hash-based and vector-based detection.
    
    - Hash check: detects exact byte-for-byte duplicates
    - Vector check: detects semantic similarity (paraphrasing)
    
    Only the document owner can check their own documents.
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document.uploaded_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to check this document")
    
    # Run both checks
    hash_result = hash_check(document.content_hash, document_id, db) if document.content_hash else {
        "is_duplicate": False,
        "matched_document_id": None
    }
    
    vector_result = vector_check(document_id, db)
    
    return PlagiarismResult(
        document_id=document.id,
        filename=document.filename,
        hash_check=HashCheckResult(**hash_result),
        vector_check=VectorCheckResult(**vector_result)
    )
