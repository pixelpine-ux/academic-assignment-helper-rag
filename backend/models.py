from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func, JSON, Boolean
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    assignments = relationship("Assignment", back_populates="creator")
    documents = relationship("Document", back_populates="uploader")

class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text, nullable=True)
    due_date = Column(DateTime, nullable=True)
    status = Column(String, default="draft")
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    creator = relationship("User", back_populates="assignments")
    documents = relationship("Document", back_populates="assignment")

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    content = Column(Text)
    doc_metadata = Column(JSON, nullable=True)
    content_hash = Column(String, nullable=True, index=True)

    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=True)

    uploader = relationship("User", back_populates="documents")
    assignment = relationship("Assignment", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    created_at = Column(DateTime, default=func.now())


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    chunk_text = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)  # position in the document (0, 1, 2...)
    embedding = Column(Vector(1536), nullable=False)

    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    document = relationship("Document", back_populates="chunks")