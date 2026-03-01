import os
import sys
import time
import psycopg2
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:securepassword@localhost:5432/academic_rag")

def wait_for_db(max_retries=30, delay=1):
    """Wait for database to be ready"""
    for i in range(max_retries):
        try:
            conn = psycopg2.connect(DATABASE_URL)
            conn.close()
            print(f"✅ Database connection successful")
            return True
        except psycopg2.OperationalError:
            print(f"⏳ Waiting for database... ({i+1}/{max_retries})")
            time.sleep(delay)
    raise Exception("❌ Database connection failed after maximum retries")

def check_pgvector():
    """Verify pgvector extension is installed"""
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM pg_extension WHERE extname = 'vector'"))
        if result.fetchone():
            print("✅ pgvector extension is installed")
            return True
        else:
            print("⚠️  pgvector extension not found, attempting to install...")
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
            print("✅ pgvector extension installed")
            return True

def apply_migrations():
    """Apply database schema migrations"""
    from models import Base
    from database import engine
    
    Base.metadata.create_all(bind=engine)
    print("✅ Database schema applied")

def create_test_user():
    """Create a test user account"""
    from database import SessionLocal
    from models import User
    from app.core.auth import get_password_hash
    
    db = SessionLocal()
    try:
        existing_user = db.query(User).filter(User.email == "test@example.com").first()
        if existing_user:
            print("ℹ️  Test user already exists")
            return existing_user.id
        
        test_user = User(
            email="test@example.com",
            hashed_password=get_password_hash("testpass123"),
            is_active=True
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        print(f"✅ Test user created (ID: {test_user.id})")
        return test_user.id
    finally:
        db.close()

def setup_all():
    """Run all setup steps"""
    print("\n🚀 Starting Pre-Test Setup...\n")
    
    print("Phase 1: Docker Containers")
    print("=" * 50)
    wait_for_db()
    
    print("\nPhase 2: Database Connection")
    print("=" * 50)
    check_pgvector()
    
    print("\nPhase 3: Schema Migration")
    print("=" * 50)
    apply_migrations()
    
    print("\nPhase 4: Test User Account")
    print("=" * 50)
    user_id = create_test_user()
    
    print("\n" + "=" * 50)
    print("✅ Pre-Test Setup Complete!")
    print("=" * 50)
    print(f"\nTest User Credentials:")
    print(f"  Email: test@example.com")
    print(f"  Password: testpass123")
    print(f"  User ID: {user_id}\n")

if __name__ == "__main__":
    setup_all()
