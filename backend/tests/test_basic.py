import pytest
import sys
import os
from sqlalchemy import text

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import SessionLocal
from models import User

def test_database_connection():
    """Test that we can connect to the database"""
    db = SessionLocal()
    try:
        # Simple query to test connection
        result = db.execute(text("SELECT 1"))
        assert result.fetchone()[0] == 1
    finally:
        db.close()

def test_user_exists():
    """Test that our test user was created"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "test@example.com").first()
        assert user is not None
        assert user.email == "test@example.com"
        assert user.is_active == True
    finally:
        db.close()