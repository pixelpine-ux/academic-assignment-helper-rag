from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Document, DocumentChunk
from typing import Optional, Dict, Any

SIMILARITY_THRESHOLD = 0.92


def hash_check(content_hash: str, document_id: int, db: Session) -> Dict[str, Any]:
    """
    Check if another document with the same SHA-256 hash exists.
    Excludes the document being checked (self-exclusion).
    
    Returns:
        {
            "is_duplicate": bool,
            "matched_document_id": int or None
        }
    """
    match = (
        db.query(Document)
        .filter(
            Document.content_hash == content_hash,
            Document.id != document_id
        )
        .first()
    )
    
    return {
        "is_duplicate": match is not None,
        "matched_document_id": match.id if match else None
    }


def vector_check(document_id: int, db: Session) -> Dict[str, Any]:
    """
    Check semantic similarity against all other documents using chunk embeddings.
    
    Strategy:
    - Get all chunks for the target document
    - For each chunk, find the most similar chunk from OTHER documents
    - Average the top similarity scores across all chunks
    - If average > threshold, flag as potential plagiarism
    
    Self-exclusion: chunks from document_id are excluded from search.
    Cross-user: searches across all users' documents.
    
    Returns:
        {
            "is_flagged": bool,
            "similarity_score": float (0.0 to 1.0),
            "matched_document_id": int or None
        }
    """
    target_chunks = (
        db.query(DocumentChunk)
        .filter(DocumentChunk.document_id == document_id)
        .all()
    )
    
    if not target_chunks:
        return {
            "is_flagged": False,
            "similarity_score": 0.0,
            "matched_document_id": None
        }
    
    similarity_scores = []
    matched_documents = {}
    
    for chunk in target_chunks:
        # Find the most similar chunk from OTHER documents
        most_similar = (
            db.query(
                DocumentChunk.document_id,
                (1 - DocumentChunk.embedding.cosine_distance(chunk.embedding)).label("similarity")
            )
            .filter(DocumentChunk.document_id != document_id)
            .order_by(DocumentChunk.embedding.cosine_distance(chunk.embedding))
            .first()
        )
        
        if most_similar:
            similarity_scores.append(most_similar.similarity)
            doc_id = most_similar.document_id
            matched_documents[doc_id] = matched_documents.get(doc_id, 0) + most_similar.similarity
    
    if not similarity_scores:
        return {
            "is_flagged": False,
            "similarity_score": 0.0,
            "matched_document_id": None
        }
    
    avg_similarity = sum(similarity_scores) / len(similarity_scores)
    
    # Find the document with the highest cumulative similarity
    best_match_id = max(matched_documents, key=matched_documents.get) if matched_documents else None
    
    return {
        "is_flagged": avg_similarity >= SIMILARITY_THRESHOLD,
        "similarity_score": round(avg_similarity, 4),
        "matched_document_id": best_match_id
    }
