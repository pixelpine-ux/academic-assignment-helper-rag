import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
from database import engine, get_db
import models
from app.api import auth, assignments, documents
from app.core.dependencies import get_current_user

load_dotenv()

app = FastAPI(
    title="Academic Assignment Helper API",
    description="RAG-powered academic support system with assignment analysis and plagiarism detection",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(assignments.router, dependencies=[Depends(get_current_user)])
app.include_router(documents.router, dependencies=[Depends(get_current_user)])

@app.on_event("startup")
def on_startup():
    # Enable pgvector extension
    with engine.connect() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        connection.commit()
    
    # Create database tables
    models.Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {
        "message": "Academic Assignment Helper Backend is Running",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health/db")
def check_db_connection(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT 1"))
        return {"status": "healthy", "database_response": result.scalar()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")