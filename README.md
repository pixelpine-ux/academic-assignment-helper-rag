# Academic Assignment Helper & Plagiarism Detector (RAG-Powered)

## 📖 Overview
A production-grade academic support system that automates assignment analysis using a Retrieval-Augmented Generation (RAG) architecture. It integrates a secure FastAPI backend, PostgreSQL with vector search (pgvector), and n8n automation workflows.

## 🏗 Tech Stack
- **Backend:** FastAPI (Python 3.11)
- **Database:** PostgreSQL 16 + pgvector
- **Automation:** n8n
- **Containerization:** Docker & Docker Compose
- **AI/ML:** OpenAI Embeddings (or local LLM)

## 🚀 Getting Started

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

## 📝 License
MIT
