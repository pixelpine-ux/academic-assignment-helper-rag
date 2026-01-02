import os
from fastapi import FastAPI
from sqlalchemy import create_engine, text

app = FastAPI(title="Academic RAG API")

# Get DB URL from environment variables (defined in docker-compose.yml)
DATABASE_URL = os.getenv("DATABASE_URL")

@app.get("/")
def read_root():
    return {"message": "Academic Assignment Helper Backend is Running"}

@app.get("/health/db")
def check_db_connection():
    """
    Checks if the backend can successfully connect to the database.
    """
    try:
        if not DATABASE_URL:
            return {"status": "error", "detail": "DATABASE_URL not set"}
        
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            return {"status": "healthy", "database_response": result.scalar()}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}