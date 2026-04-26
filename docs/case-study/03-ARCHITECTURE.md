# System Architecture & Technical Design

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                             │
│  (Web App / Mobile App / Postman / Any HTTP Client)             │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/REST
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Auth API   │  │ Document API │  │  Query API   │          │
│  │  (JWT/Login) │  │ (Upload/CRUD)│  │  (RAG Q&A)   │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                  │                  │                  │
│  ┌──────▼──────────────────▼──────────────────▼───────┐         │
│  │              Service Layer                          │         │
│  │  • chunking_service.py                              │         │
│  │  • embedding_service.py                             │         │
│  │  • vector_search_service.py                         │         │
│  │  • llm_service.py                                   │         │
│  │  • plagiarism_service.py (coming)                   │         │
│  └──────────────────────┬──────────────────────────────┘         │
└─────────────────────────┼────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                  PostgreSQL + pgvector                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │  users   │  │documents │  │ document │  │assignments│        │
│  │          │  │          │  │  _chunks │  │          │        │
│  │  • id    │  │  • id    │  │  • id    │  │  • id    │        │
│  │  • email │  │  • title │  │  • chunk │  │  • title │        │
│  │  • hash  │  │  • user  │  │  • embed │  │  • user  │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
│                                    │                             │
│                                    ▼                             │
│                          Vector Search (pgvector)                │
│                          Cosine Similarity (<=>)                 │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      OpenAI API                                  │
│  • text-embedding-3-small  (1536-dim vectors)                   │
│  • gpt-3.5-turbo           (answer generation)                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow Diagrams

### 1. Document Upload Flow

```
User uploads document.txt
         │
         ▼
┌────────────────────────────────────────────────────────┐
│ POST /documents/upload                                 │
│  1. Verify JWT token → get current_user               │
│  2. Read file content                                  │
│  3. Create Document record (db.flush() for ID)        │
└────────┬───────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────────────────┐
│ chunking_service.chunk_text(content)                   │
│  • Split into 500-token chunks                         │
│  • 100-token overlap between chunks                    │
│  • Returns: ["chunk_0", "chunk_1", ..., "chunk_n"]    │
└────────┬───────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────────────────┐
│ For each chunk:                                        │
│   embedding_service.get_embedding(chunk_text)          │
│   • Call OpenAI API                                    │
│   • Returns: [1536 floats]                             │
│   • Create DocumentChunk record with embedding         │
└────────┬───────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────────────────┐
│ db.commit()                                            │
│  • Document + all chunks saved atomically              │
│  • Return: DocumentResponse with chunk_count           │
└────────────────────────────────────────────────────────┘
```

### 2. RAG Query Flow

```
User asks: "What is the main argument?"
         │
         ▼
┌────────────────────────────────────────────────────────┐
│ POST /query                                            │
│  1. Verify JWT token → get current_user               │
│  2. Receive question text                              │
└────────┬───────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────────────────┐
│ embedding_service.get_embedding(question)              │
│  • Convert question to vector: [1536 floats]           │
└────────┬───────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────────────────┐
│ vector_search_service.search_similar_chunks()          │
│  • SQL: ORDER BY embedding <=> question_embedding      │
│  • Filter: WHERE document.uploaded_by = user_id        │
│  • LIMIT 5 (top 5 most similar chunks)                 │
│  • Returns: [chunk1, chunk2, chunk3, chunk4, chunk5]   │
└────────┬───────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────────────────┐
│ llm_service.generate_answer()                          │
│  • Build prompt:                                       │
│    - System: "Answer using ONLY these sources"         │
│    - Sources: [chunk1, chunk2, ...]                    │
│    - Question: "What is the main argument?"            │
│  • Call GPT-3.5-turbo (temperature=0.2)                │
│  • Returns: Answer with [Source N] citations           │
└────────┬───────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────────────────┐
│ Return QueryResponse                                   │
│  • answer: "The main argument is... [Source 1]"        │
│  • source_document_ids: [doc_id_1, doc_id_2]           │
│  • chunks_used: 5                                      │
└────────────────────────────────────────────────────────┘
```

### 3. Authentication Flow

```
User registers/logs in
         │
         ▼
┌────────────────────────────────────────────────────────┐
│ POST /auth/register                                    │
│  • Hash password with bcrypt (cost factor 12)          │
│  • Store user in database                              │
│  • Return: JWT token (expires in 30 days)             │
└────────────────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────────────────┐
│ All subsequent requests include:                       │
│  Authorization: Bearer <JWT_TOKEN>                     │
└────────┬───────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────────────────┐
│ get_current_user() dependency                          │
│  • Decode JWT token                                    │
│  • Verify signature and expiration                     │
│  • Load user from database                             │
│  • Inject into endpoint as current_user                │
└────────────────────────────────────────────────────────┘
```

---

## 🗄️ Database Schema

```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Documents table
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    uploaded_by INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Document chunks table (vector storage)
CREATE TABLE document_chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    chunk_text TEXT NOT NULL,
    embedding VECTOR(1536) NOT NULL,  -- pgvector type
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(document_id, chunk_index)
);

-- Create vector similarity index (HNSW for performance)
CREATE INDEX idx_chunks_embedding ON document_chunks 
USING hnsw (embedding vector_cosine_ops);

-- Assignments table
CREATE TABLE assignments (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    due_date TIMESTAMP,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Key Relationships
- `users` 1:N `documents` (one user uploads many documents)
- `documents` 1:N `document_chunks` (one document has many chunks)
- `users` 1:N `assignments` (one user has many assignments)

### Cascade Rules
- Delete user → deletes all their documents, chunks, and assignments
- Delete document → deletes all its chunks (orphan prevention)

---

## 🔧 Service Layer Architecture

### Separation of Concerns

Each service has ONE responsibility:

```python
# chunking_service.py
def chunk_text(text: str) -> List[str]:
    """Text in → List of chunk strings out"""
    # Knows: How to split text into chunks
    # Doesn't know: What embeddings are, what the database is

# embedding_service.py
def get_embedding(text: str) -> List[float]:
    """Text in → 1536-dimensional vector out"""
    # Knows: How to call OpenAI API
    # Doesn't know: What chunks are, what the database is

# vector_search_service.py
def search_similar_chunks(question: str, user_id: int) -> List[Chunk]:
    """Question in → Top 5 similar chunks out"""
    # Knows: How to do vector search with pgvector
    # Doesn't know: How embeddings are generated, what the LLM does

# llm_service.py
def generate_answer(question: str, chunks: List[Chunk]) -> str:
    """Question + context in → Grounded answer out"""
    # Knows: How to prompt GPT and get answers
    # Doesn't know: How chunks were retrieved, what the database is
```

### Why This Matters
- **Testability:** Each service can be unit tested in isolation
- **Maintainability:** Change one service without breaking others
- **Swappability:** Replace OpenAI with local LLM by changing one file
- **Clarity:** Each file has a clear, single purpose

---

## 🔐 Security Architecture

### 1. Authentication (JWT)
```
Stateless tokens → No server-side session storage
Signed with secret key → Tamper-proof
30-day expiration → Automatic logout
bcrypt password hashing → Brute-force resistant
```

### 2. Data Scoping (Multi-Tenant Isolation)
```python
# Every query filters by user
documents = db.query(Document).filter(
    Document.uploaded_by == current_user.id
).all()

# Vector search only searches user's documents
chunks = db.query(DocumentChunk).join(Document).filter(
    Document.uploaded_by == user_id
).order_by(...)
```

**Result:** Users can NEVER see other users' data.

### 3. Input Validation
- Pydantic schemas validate all request bodies
- File size limits on uploads
- SQL injection prevention (SQLAlchemy ORM)
- XSS prevention (no HTML rendering)

---

## 🚀 Deployment Architecture

### Docker Compose Setup

```yaml
services:
  postgres:
    image: pgvector/pgvector:pg16
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    
  backend:
    build: ./backend
    depends_on:
      - postgres
    environment:
      - DATABASE_URL=postgresql://...
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    ports:
      - "8000:8000"
  
  n8n:
    image: n8nio/n8n
    depends_on:
      - postgres
    ports:
      - "5678:5678"
```

### Why Docker?
- **Portability:** Runs anywhere (dev, staging, prod)
- **Consistency:** Same environment on all machines
- **Isolation:** Services don't conflict
- **Scalability:** Easy to add replicas

---

## 📊 Technical Decisions Log

| Decision | What | Why |
|----------|------|-----|
| **Framework** | FastAPI | Async support, auto docs, type safety, performance |
| **Database** | PostgreSQL | ACID compliance, mature, pgvector support |
| **Vector Store** | pgvector | No extra infrastructure, production-ready, cost-effective |
| **Embedding Model** | text-embedding-3-small | 1536 dims, $0.02/1M tokens, high quality |
| **LLM** | gpt-3.5-turbo | Fast, affordable, sufficient for MVP |
| **Auth** | JWT (stateless) | REST APIs are stateless, scales horizontally |
| **Password Hash** | bcrypt | Industry standard, intentionally slow (brute-force resistant) |
| **Chunk Size** | 500 tokens | Balances context richness vs. retrieval precision |
| **Chunk Overlap** | 100 tokens | Prevents meaning loss at boundaries |
| **Tokenizer** | tiktoken | Matches OpenAI's tokenizer exactly |
| **Temperature** | 0.2 | Low randomness for factual Q&A |
| **Top-K Retrieval** | 5 chunks | Enough context without overwhelming the LLM |

---

## 🔮 Future Architecture Enhancements

### Planned Improvements
1. **Caching Layer** - Redis for frequently accessed embeddings
2. **Async Processing** - Celery for background document processing
3. **Rate Limiting** - Prevent API abuse
4. **Monitoring** - Prometheus + Grafana for metrics
5. **Load Balancing** - Multiple backend replicas
6. **CDN** - For document downloads
7. **Backup Strategy** - Automated PostgreSQL backups

### Scalability Path
```
Current: Single backend + single database
  ↓
Next: Multiple backend replicas + single database
  ↓
Future: Multiple backends + read replicas + caching
  ↓
Scale: Kubernetes + managed PostgreSQL + Redis cluster
```

---

## 🎓 What This Architecture Demonstrates

### To Hiring Managers
1. **System Design Thinking** - Not just code, but architecture
2. **Separation of Concerns** - Clean, maintainable structure
3. **Security Awareness** - Multi-tenant isolation, auth, validation
4. **Scalability** - Stateless design, Docker, horizontal scaling
5. **Production Readiness** - Error handling, transactions, cascade rules

### Technical Depth
- Understanding of vector databases (pgvector)
- Knowledge of RAG architecture patterns
- RESTful API design principles
- Database schema design and relationships
- Service-oriented architecture

---

*Next: See [04-IMPLEMENTATION.md](./04-IMPLEMENTATION.md) for code examples and key implementations.*
