"""
WHY: Comprehensive test coverage ensures API reliability
- Tests cover happy paths, edge cases, and security scenarios
- Each test is isolated and can run independently
- Uses pytest fixtures for clean test setup/teardown
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from database import Base, get_db
from main import app
from models import User, Document, Assignment
from app.core.auth import get_password_hash

# WHY: In-memory SQLite for fast test execution without affecting production DB
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    """WHY: Fresh database for each test ensures isolation"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    """WHY: Override get_db dependency to use test database"""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(db):
    """WHY: Reusable test user fixture to avoid duplication"""
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("TestPassword123"),
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def auth_headers(client, test_user):
    """WHY: Reusable authentication headers for protected endpoints"""
    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "TestPassword123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# ============= GET /users/me Tests =============

def test_get_profile_success(client, test_user, auth_headers):
    """WHY: Verify authenticated user can retrieve their profile"""
    response = client.get("/users/me", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email
    assert data["id"] == test_user.id
    assert data["is_active"] == True
    assert "hashed_password" not in data  # WHY: Never expose password hash

def test_get_profile_unauthorized(client):
    """WHY: Verify endpoint is protected and returns 401 without auth"""
    response = client.get("/users/me")
    assert response.status_code == 403  # WHY: FastAPI HTTPBearer returns 403

def test_get_profile_invalid_token(client):
    """WHY: Verify invalid JWT tokens are rejected"""
    response = client.get("/users/me", headers={"Authorization": "Bearer invalid_token"})
    assert response.status_code == 401

# ============= GET /users/me/statistics Tests =============

def test_get_statistics_empty(client, test_user, auth_headers):
    """WHY: New user should have zero statistics"""
    response = client.get("/users/me/statistics", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_documents"] == 0
    assert data["total_assignments"] == 0
    assert data["plagiarism_checks_run"] == 0
    assert data["recent_activity_count"] == 0

def test_get_statistics_with_data(client, test_user, auth_headers, db):
    """WHY: Verify statistics calculation with real data"""
    # Create test data
    assignment = Assignment(
        title="Test Assignment",
        created_by=test_user.id,
        status="active"
    )
    db.add(assignment)
    db.commit()
    
    # WHY: Add documents with different scenarios
    doc1 = Document(
        filename="doc1.pdf",
        content="Test content",
        uploaded_by=test_user.id,
        content_hash="hash123",  # WHY: Has hash = plagiarism check was run
        created_at=datetime.utcnow()
    )
    doc2 = Document(
        filename="doc2.pdf",
        content="Test content 2",
        uploaded_by=test_user.id,
        content_hash="hash456",
        created_at=datetime.utcnow() - timedelta(days=10)  # WHY: Old, not recent
    )
    doc3 = Document(
        filename="doc3.pdf",
        content="Test content 3",
        uploaded_by=test_user.id,
        content_hash=None,  # WHY: No plagiarism check
        created_at=datetime.utcnow()
    )
    db.add_all([doc1, doc2, doc3])
    db.commit()
    
    response = client.get("/users/me/statistics", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_documents"] == 3
    assert data["total_assignments"] == 1
    assert data["plagiarism_checks_run"] == 2  # WHY: Only doc1 and doc2 have hashes
    assert data["recent_activity_count"] == 2  # WHY: Only doc1 and doc3 in last 7 days

def test_get_statistics_user_isolation(client, test_user, auth_headers, db):
    """WHY: Verify users can't see other users' statistics"""
    # Create another user with data
    other_user = User(
        email="other@example.com",
        hashed_password=get_password_hash("Password123"),
        is_active=True
    )
    db.add(other_user)
    db.commit()
    
    other_doc = Document(
        filename="other.pdf",
        content="Other content",
        uploaded_by=other_user.id,
        content_hash="other_hash"
    )
    db.add(other_doc)
    db.commit()
    
    response = client.get("/users/me/statistics", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_documents"] == 0  # WHY: Should not count other user's docs

# ============= PUT /users/me/password Tests =============

def test_change_password_success(client, test_user, auth_headers):
    """WHY: Verify successful password change flow"""
    response = client.put("/users/me/password", headers=auth_headers, json={
        "current_password": "TestPassword123",
        "new_password": "NewPassword456"
    })
    
    assert response.status_code == 204  # WHY: 204 No Content for successful update
    
    # WHY: Verify new password works by logging in
    login_response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "NewPassword456"
    })
    assert login_response.status_code == 200

def test_change_password_wrong_current(client, test_user, auth_headers):
    """WHY: Security check - wrong current password should fail"""
    response = client.put("/users/me/password", headers=auth_headers, json={
        "current_password": "WrongPassword",
        "new_password": "NewPassword456"
    })
    
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()

def test_change_password_same_as_current(client, test_user, auth_headers):
    """WHY: Prevent no-op updates - new password must be different"""
    response = client.put("/users/me/password", headers=auth_headers, json={
        "current_password": "TestPassword123",
        "new_password": "TestPassword123"
    })
    
    assert response.status_code == 400
    assert "different" in response.json()["detail"].lower()

def test_change_password_weak_password(client, test_user, auth_headers):
    """WHY: Enforce password strength requirements"""
    # WHY: Test too short
    response = client.put("/users/me/password", headers=auth_headers, json={
        "current_password": "TestPassword123",
        "new_password": "short"
    })
    assert response.status_code == 422
    
    # WHY: Test no digits
    response = client.put("/users/me/password", headers=auth_headers, json={
        "current_password": "TestPassword123",
        "new_password": "NoDigitsHere"
    })
    assert response.status_code == 422
    
    # WHY: Test no letters
    response = client.put("/users/me/password", headers=auth_headers, json={
        "current_password": "TestPassword123",
        "new_password": "12345678"
    })
    assert response.status_code == 422

def test_change_password_unauthorized(client):
    """WHY: Verify endpoint is protected"""
    response = client.put("/users/me/password", json={
        "current_password": "TestPassword123",
        "new_password": "NewPassword456"
    })
    assert response.status_code == 403
