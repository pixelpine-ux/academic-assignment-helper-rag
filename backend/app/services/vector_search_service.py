from sqlalchemy.orm import Session
from sqlalchemy import select
from models import DocumentChunk, Document
from app.services.embedding_service import get_embedding
from typing import List

TOP_K = 5  # number of chunks to retrieve


def search_chunks(question: str, user_id: int, db: Session) -> List[DocumentChunk]:
    """
    Embed the question and return the TOP_K most similar chunks owned by user_id.
    Uses pgvector's cosine distance operator (<=>).
    """
    question_embedding = get_embedding(question)

    results = (
        db.query(DocumentChunk)
        .join(Document, DocumentChunk.document_id == Document.id)
        .filter(Document.uploaded_by == user_id)
        .order_by(DocumentChunk.embedding.cosine_distance(question_embedding))
        .limit(TOP_K)
        .all()
    )

    return results
