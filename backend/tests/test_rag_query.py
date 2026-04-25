import pytest
from unittest.mock import patch, MagicMock

FAKE_EMBEDDING = [0.01] * 1536  # valid 1536-dim vector, no real API call


# ── Upload endpoint ────────────────────────────────────────────────────────────

@patch("app.api.documents.get_embedding", return_value=FAKE_EMBEDDING)
@patch("app.api.documents.chunk_text", return_value=["chunk one", "chunk two"])
def test_upload_creates_document_and_chunks(mock_chunk, mock_embed, client, auth_headers):
    response = client.post(
        "/documents/upload",
        files={"file": ("essay.txt", b"This is a test essay.", "text/plain")},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "essay.txt"
    assert data["uploaded_by"] is not None
    # chunk_text was called once, get_embedding called once per chunk
    assert mock_chunk.call_count == 1
    assert mock_embed.call_count == 2


def test_upload_requires_auth(client):
    response = client.post(
        "/documents/upload",
        files={"file": ("essay.txt", b"content", "text/plain")},
    )
    assert response.status_code == 403


# ── Query endpoint ─────────────────────────────────────────────────────────────

@patch("app.api.documents.get_embedding", return_value=FAKE_EMBEDDING)
@patch("app.api.documents.chunk_text", return_value=["The main argument is X."])
@patch("app.api.query.search_chunks", return_value=[MagicMock(document_id=1, chunk_index=0, chunk_text="The main argument is X.")])
@patch(
    "app.api.query.generate_answer",
    return_value={
        "answer": "The main argument is X [Source 1].",
        "source_document_ids": [1],
        "chunks_used": 1,
    },
)
def test_rag_query_returns_grounded_answer(
    mock_answer, mock_search, mock_chunk, mock_upload_embed, client, auth_headers
):
    client.post(
        "/documents/upload",
        files={"file": ("essay.txt", b"The main argument is X.", "text/plain")},
        headers=auth_headers,
    )

    response = client.post(
        "/query/",
        json={"question": "What is the main argument?"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["question"] == "What is the main argument?"
    assert "answer" in data
    assert isinstance(data["source_document_ids"], list)
    assert data["chunks_used"] >= 1


def test_query_rejects_empty_question(client, auth_headers):
    response = client.post(
        "/query/",
        json={"question": "   "},
        headers=auth_headers,
    )
    assert response.status_code == 400


def test_query_requires_auth(client):
    response = client.post("/query/", json={"question": "What is this about?"})
    assert response.status_code == 403


# ── Duplicate detection on upload ──────────────────────────────────────────────

@patch("app.api.documents.get_embedding", return_value=FAKE_EMBEDDING)
@patch("app.api.documents.chunk_text", return_value=["some chunk"])
def test_upload_duplicate_returns_409(mock_chunk, mock_embed, client, auth_headers):
    file_content = b"Identical content for duplicate test."
    client.post(
        "/documents/upload",
        files={"file": ("original.txt", file_content, "text/plain")},
        headers=auth_headers,
    )
    response = client.post(
        "/documents/upload",
        files={"file": ("copy.txt", file_content, "text/plain")},
        headers=auth_headers,
    )
    assert response.status_code == 409
    data = response.json()
    assert "matched_document_id" in data["detail"]
    assert data["detail"]["message"] == "Exact duplicate detected."


@patch("app.api.query.search_chunks", return_value=[])
def test_query_404_when_no_documents(mock_search, client, auth_headers):
    """A user with no uploaded documents should get a 404, not a 500."""
    response = client.post(
        "/query/",
        json={"question": "What is this about?"},
        headers=auth_headers,
    )
    assert response.status_code == 404
