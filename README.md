# Academic Assignment Helper & Plagiarism Detector (RAG-Powered)

## Overview
A production-grade academic support system that automates assignment analysis using a Retrieval-Augmented Generation (RAG) architecture. It integrates a secure FastAPI backend, PostgreSQL with vector search (pgvector), and n8n automation workflows.

## Tech Stack
- **Backend:** FastAPI (Python 3.11)
- **Database:** PostgreSQL 16 + pgvector
- **Automation:** n8n
- **Containerization:** Docker & Docker Compose
- **AI/ML:** OpenAI Embeddings (or local LLM)
- **File Processing:** PyPDF2, python-docx (PDF, DOCX, TXT support)

## Features
- **Document Upload:** Supports PDF, DOCX, and TXT files (max 10MB)
- **RAG-Powered Q&A:** Ask questions about uploaded documents
- **Plagiarism Detection:** Hash-based and semantic similarity checks
- **Multi-Tenant Security:** User isolation with JWT authentication
- **Vector Search:** Fast semantic search with pgvector

##  Getting Started

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)

### Quick Start
1. Clone the repository.
2. Copy the environment file:
   ```bash
   cp .env.example .env
   ```
3. Start the services:
   ```bash
   docker-compose up -d
   ```
4. Access the API documentation at `http://localhost:8000/docs`

### Supported File Formats
- **PDF** (.pdf) - Extracted using PyPDF2
- **Word Documents** (.docx) - Extracted using python-docx
- **Text Files** (.txt) - UTF-8 and Latin-1 encoding
- **File Size Limit:** 10MB per file

##  License
MIT
