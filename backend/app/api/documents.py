import hashlib
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models import Document, DocumentChunk, User
from app.schemas.document import DocumentCreate, Document as DocumentSchema
from app.core.dependencies import get_current_user
from app.services.chunking_service import chunk_text
from app.services.embedding_service import get_embedding

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/upload", response_model=DocumentSchema)
async def upload_document(
    file: UploadFile = File(...),
    assignment_id: Optional[int] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    content = await file.read()
    content_str = content.decode('utf-8')
    content_hash = hashlib.sha256(content).hexdigest()

    db_document = Document(
        filename=file.filename,
        content=content_str,
        content_hash=content_hash,
        assignment_id=assignment_id,
        uploaded_by=current_user.id,
        doc_metadata={"size": len(content), "content_type": file.content_type}
    )
    db.add(db_document)
    db.flush()  # get db_document.id without committing

    chunks = chunk_text(content_str)
    for index, chunk in enumerate(chunks):
        embedding = get_embedding(chunk)
        db.add(DocumentChunk(
            document_id=db_document.id,
            chunk_text=chunk,
            chunk_index=index,
            embedding=embedding
        ))

    db.commit()
    db.refresh(db_document)
    return db_document

@router.get("/", response_model=List[DocumentSchema])
def get_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Document).filter(Document.uploaded_by == current_user.id).offset(skip).limit(limit).all()

@router.get("/{document_id}", response_model=DocumentSchema)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.uploaded_by == current_user.id
    ).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.uploaded_by == current_user.id
    ).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(document)
    db.commit()
    return {"message": "Document deleted successfully"}