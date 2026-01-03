from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from database import engine, get_db
import models

app = FastAPI(title="Academic RAG API")

@app.on_event("startup")
def on_startup():
    # 1. Enable the pgvector extension in the database
    with engine.connect() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        connection.commit()
    
    # 2. Create the database tables defined in models.py
    models.Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "Academic Assignment Helper Backend is Running"}

@app.get("/health/db")
def check_db_connection(db: Session = Depends(get_db)):
    """
    Checks if the backend can successfully connect to the database.
    """
    try:
        # Execute a simple query using the session
        result = db.execute(text("SELECT 1"))
        return {"status": "healthy", "database_response": result.scalar()}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}