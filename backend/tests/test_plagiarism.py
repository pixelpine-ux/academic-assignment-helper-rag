import pytest
from unittest.mock import patch
from models import Document, DocumentChunk


def test_exact_hash_match(client, auth_headers, db, test_user):
    """Test that exact duplicate (same hash) is detected"""
    
    # Create two documents with the same hash
    doc1 = Document(
        filename="original.txt",
        content="This is the original essay content.",
        content_hash="abc123hash",
        uploaded_by=test_user.id
    )
    doc2 = Document(
        filename="duplicate.txt",
        content="This is the original essay content.",
        content_hash="abc123hash",
        uploaded_by=test_user.id
    )
    db.add(doc1)
    db.add(doc2)
    db.commit()
    db.refresh(doc1)
    db.refresh(doc2)
    
    # Check doc2 for plagiarism
    response = client.post(
        f"/documents/{doc2.id}/check-plagiarism",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["document_id"] == doc2.id
    assert data["hash_check"]["is_duplicate"] is True
    assert data["hash_check"]["matched_document_id"] == doc1.id


def test_semantic_similarity_match(client, auth_headers, db, test_user):
    """Test that paraphrased content (high vector similarity) is flagged"""
    
    # Mock embeddings to return controlled vectors
    with patch("app.services.embedding_service.get_embedding") as mock_embed:
        # Original document gets embedding [1.0, 0.0, 0.0, ...]
        # Paraphrased document gets very similar embedding [0.98, 0.02, 0.0, ...]
        original_embedding = [1.0] + [0.0] * 1535
        similar_embedding = [0.98, 0.02] + [0.0] * 1534
        
        mock_embed.side_effect = [original_embedding, similar_embedding]
        
        # Upload original document
        response1 = client.post(
            "/documents/upload",
            files={"file": ("original.txt", b"The main argument is X.", "text/plain")},
            headers=auth_headers
        )
        assert response1.status_code == 200
        doc1_id = response1.json()["id"]
        
        # Upload paraphrased document
        response2 = client.post(
            "/documents/upload",
            files={"file": ("paraphrase.txt", b"The primary claim is X.", "text/plain")},
            headers=auth_headers
        )
        assert response2.status_code == 200
        doc2_id = response2.json()["id"]
    
    # Check doc2 for plagiarism
    response = client.post(
        f"/documents/{doc2_id}/check-plagiarism",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["document_id"] == doc2_id
    assert data["hash_check"]["is_duplicate"] is False  # Different content
    assert data["vector_check"]["is_flagged"] is True   # High similarity
    assert data["vector_check"]["similarity_score"] >= 0.92
    assert data["vector_check"]["matched_document_id"] == doc1_id


def test_self_exclusion(client, auth_headers, db, test_user):
    """Test that a document doesn't match itself"""
    
    with patch("app.services.embedding_service.get_embedding") as mock_embed:
        mock_embed.return_value = [1.0] + [0.0] * 1535
        
        # Upload a document
        response = client.post(
            "/documents/upload",
            files={"file": ("essay.txt", b"Unique content here.", "text/plain")},
            headers=auth_headers
        )
        assert response.status_code == 200
        doc_id = response.json()["id"]
    
    # Check the same document for plagiarism
    response = client.post(
        f"/documents/{doc_id}/check-plagiarism",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Should not match itself
    assert data["hash_check"]["is_duplicate"] is False
    assert data["vector_check"]["is_flagged"] is False


def test_no_match_unique_content(client, auth_headers, db, test_user):
    """Test that unique content returns clean results"""
    
    with patch("app.services.embedding_service.get_embedding") as mock_embed:
        # Two completely different embeddings
        embedding1 = [1.0, 0.0] + [0.0] * 1534
        embedding2 = [0.0, 1.0] + [0.0] * 1534
        
        mock_embed.side_effect = [embedding1, embedding2]
        
        # Upload two unrelated documents
        response1 = client.post(
            "/documents/upload",
            files={"file": ("doc1.txt", b"Content about topic A.", "text/plain")},
            headers=auth_headers
        )
        assert response1.status_code == 200
        
        response2 = client.post(
            "/documents/upload",
            files={"file": ("doc2.txt", b"Content about topic B.", "text/plain")},
            headers=auth_headers
        )
        assert response2.status_code == 200
        doc2_id = response2.json()["id"]
    
    # Check doc2 for plagiarism
    response = client.post(
        f"/documents/{doc2_id}/check-plagiarism",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["hash_check"]["is_duplicate"] is False
    assert data["vector_check"]["is_flagged"] is False
    assert data["vector_check"]["similarity_score"] < 0.92


def test_authorization_check(client, auth_headers, db, test_user):
    """Test that users can only check their own documents"""
    
    # Create a document owned by test_user
    doc = Document(
        filename="private.txt",
        content="Private content",
        content_hash="private123",
        uploaded_by=test_user.id
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    
    # Try to check with valid auth (should work)
    response = client.post(
        f"/documents/{doc.id}/check-plagiarism",
        headers=auth_headers
    )
    assert response.status_code == 200
    
    # Try to check without auth (should fail)
    response = client.post(f"/documents/{doc.id}/check-plagiarism")
    assert response.status_code == 401


def test_document_not_found(client, auth_headers):
    """Test 404 when document doesn't exist"""
    
    response = client.post(
        "/documents/99999/check-plagiarism",
        headers=auth_headers
    )
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
