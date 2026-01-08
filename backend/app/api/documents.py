from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models import Document
from app.schemas.document import DocumentCreate, Document as DocumentSchema

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/upload", response_model=DocumentSchema)
async def upload_document(
    file: UploadFile = File(...),
    assignment_id: Optional[int] = Form(None),
    db: Session = Depends(get_db)
):
    content = await file.read()
    content_str = content.decode('utf-8')
    
    doc_data = DocumentCreate(
        filename=file.filename,
        content=content_str,
        assignment_id=assignment_id,
        doc_metadata={"size": len(content), "content_type": file.content_type}
    )
    
    db_document = Document(**doc_data.dict())
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

@router.get("/", response_model=List[DocumentSchema])
def get_documents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    documents = db.query(Document).offset(skip).limit(limit).all()
    return documents

@router.get("/{document_id}", response_model=DocumentSchema)
def get_document(document_id: int, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@router.delete("/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    db.delete(document)
    db.commit()
    return {"message": "Document deleted successfully"}