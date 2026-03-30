# Project Overview

## 🎯 Quick Summary

**Project:** Academic Assignment Helper & Plagiarism Detector  
**Type:** Production-Grade REST API Backend  
**Role:** Full-Stack Developer & System Architect  
**Timeline:** [Start Date] - Present (In Active Development)  
**Status:** ✅ Milestone 1 Complete | 🚧 Milestone 2 In Progress

---

## Tech Stack

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/Python_3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)

**Backend:** FastAPI (Python 3.11)  
**Database:** PostgreSQL 16 + pgvector extension  
**AI/ML:** OpenAI Embeddings (text-embedding-3-small) + GPT-3.5-turbo  
**Automation:** n8n workflow engine  
**Containerization:** Docker & Docker Compose  
**Architecture:** RAG (Retrieval-Augmented Generation)

---

## What This Project Is

A **backend REST API** (no frontend/UI) that enables:
- Academic document upload and intelligent storage
- Semantic search using vector embeddings
- Natural language Q&A over uploaded documents
- Plagiarism detection through similarity analysis
- Multi-user authentication and data isolation

Think of it as the **engine** of an academic support system. Other applications (web apps, mobile apps) can consume this API to provide student-facing features.

---

## The One-Sentence Pitch

> "A production-style RAG-powered REST API that enables semantic document search, AI-driven Q&A, and plagiarism detection for academic content — built with FastAPI, PostgreSQL + pgvector, and OpenAI."

---

## Key Features

✅ **JWT Authentication** - Secure stateless auth with bcrypt password hashing  
✅ **Document Management** - Upload, store, and manage academic documents  
✅ **Intelligent Chunking** - Token-based text splitting with overlap for precise retrieval  
✅ **Vector Embeddings** - Semantic understanding via OpenAI embeddings  
✅ **RAG Query System** - Grounded AI answers with source citations  
✅ **User Data Scoping** - Multi-tenant security with per-user data isolation  
✅ **Dockerized Deployment** - One-command setup with Docker Compose  
🚧 **Plagiarism Detection** - Coming in Milestone 3  
🚧 **n8n Automation** - Workflow orchestration for batch processing

---

## Why This Project Matters

### The Problem
- Students need instant feedback on assignments
- Professors spend hours manually reviewing submissions
- Traditional plagiarism tools are expensive ($500+/month for Turnitin)
- Standard LLMs can't answer questions about YOUR specific documents

### The Solution
A **RAG-powered system** that:
- Retrieves relevant content from YOUR documents (not generic training data)
- Generates accurate, grounded answers with source citations
- Detects plagiarism through vector similarity search
- Costs $0 in infrastructure (open-source stack)
- Scales horizontally with stateless architecture

---

## What Makes This Different

| Traditional Approach | This RAG System |
|---------------------|-----------------|
| Generic LLM responses | Grounded in YOUR documents |
| No source citations | Every answer cites sources |
| Keyword-based search | Semantic meaning-based search |
| Expensive SaaS tools | Open-source, self-hosted |
| Single-user systems | Multi-tenant with data isolation |

---

## Project Links

- 📂 **GitHub Repository:** [Link]
- 📖 **API Documentation:** [Link to Swagger/OpenAPI]
- 🎥 **Demo Video:** [Link]
- 📊 **Architecture Diagrams:** See `docs/case-study/03-ARCHITECTURE.md`
- 🧪 **Test Results:** See `docs/case-study/06-METRICS.md`

---

## Quick Start

```bash
# Clone the repository
git clone [repo-url]

# Copy environment file
cp .env.example .env

# Start all services
docker-compose up -d

# API available at http://localhost:8000
# API docs at http://localhost:8000/docs
```

---

*Part of a comprehensive case study. See [CASE-STUDY.md](./CASE-STUDY.md) for the full technical deep dive.*
