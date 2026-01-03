from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from database import Base

class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text, nullable=True)
    due_date = Column(DateTime, nullable=True)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=func.now())
    
    # Relationship: One assignment can have many related documents
    documents = relationship("Document", back_populates="assignment")

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    content = Column(Text)
    embedding = Column(Vector(1536))  # Vector dimension for embeddings
    
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=True)
    assignment = relationship("Assignment", back_populates="documents")
    created_at = Column(DateTime, default=func.now())