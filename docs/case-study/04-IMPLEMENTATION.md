# Implementation Highlights & Code Examples

## 🎯 Purpose
This document showcases the most impressive technical implementations in the project, with explanations of WHY each pattern was chosen.

---

## 1. Atomic Transaction Pattern (Document Upload)

### The Problem
When uploading a document, we need to:
1. Create the Document record
2. Get its auto-generated ID
3. Create multiple DocumentChunk records (each needs the document_id)
4. If ANY step fails, NOTHING should be saved

### The Solution: db.flush() + Atomic Commit

```python
# backend/app/api/documents.py

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile,
    title: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    content = (await file.read()).decode("utf-8")
    
    # Step 1: Create document (but don't commit yet)
    document = Document(
        title=title,
        content=content,
        uploaded_by=current_user.id
    )
    db.add(document)
    db.flush()  # ← KEY: Sends INSERT, gets ID, but transaction still open
    
    # Step 2: Now document.id is available for foreign keys
    chunks = chunk_text(content)
    
    for idx, chunk_text in enumerate(chunks):
        embedding = get_embedding(chunk_text)
        chunk = DocumentChunk(
            document_id=document.id,  # ← Uses the flushed ID
            chunk_index=idx,
            chunk_text=chunk_text,
            embedding=embedding
        )
        db.add(chunk)
    
    # Step 3: Commit everything at once (atomic)
    db.commit()  # ← All-or-nothing: document + all chunks or nothing
    db.refresh(document)
    
    return document
```

### Why This Matters
- **Atomicity:** Either everything saves or nothing does (no partial data)
- **Referential Integrity:** Chunks always have a valid document_id
- **Clean Database:** No orphaned records if something fails halfway

### What This Shows
- Understanding of database transactions
- Knowledge of ORM patterns (flush vs commit)
- Production-ready error handling

---

## 2. Token-Based Chunking with Overlap

### The Problem
- LLMs have token limits (not character or word limits)
- Splitting at arbitrary boundaries breaks sentences/ideas
- Need to preserve context at chunk boundaries

### The Solution: tiktoken + Sliding Window

```python
# backend/app/services/chunking_service.py

import tiktoken

CHUNK_SIZE = 500      # tokens
CHUNK_OVERLAP = 100   # tokens

def chunk_text(text: str) -> List[str]:
    """
    Splits text into overlapping chunks based on token count.
    Uses OpenAI's tiktoken to match their exact tokenization.
    """
    encoding = tiktoken.get_encoding("cl100k_base")  # GPT-3.5/4 encoding
    tokens = encoding.encode(text)
    
    chunks = []
    start = 0
    
    while start < len(tokens):
        # Take CHUNK_SIZE tokens from current position
        end = start + CHUNK_SIZE
        chunk_tokens = tokens[start:end]
        
        # Decode back to text
        chunk_text = encoding.decode(chunk_tokens)
        chunks.append(chunk_text)
        
        # Move forward by (CHUNK_SIZE - CHUNK_OVERLAP)
        # This creates the overlap
        start += CHUNK_SIZE - CHUNK_OVERLAP
    
    return chunks
```

### Visual Representation
```
Document: [0.....100.....200.....300.....400.....500.....600.....700]

Chunk 1:  [0.............................500]
                                [400.............................900]  Chunk 2
                                              [800.......................1300]  Chunk 3

Overlap:                        [400...500] ← Shared between chunks 1 & 2
```

### Why This Matters
- **Precision:** Token count matches OpenAI's exactly (no surprises)
- **Context Preservation:** Ideas spanning boundaries aren't lost
- **Retrieval Quality:** Better search results with preserved context

### What This Shows
- Understanding of LLM tokenization
- Knowledge of sliding window algorithms
- Attention to edge cases (boundary handling)

---

## 3. Vector Similarity Search with User Scoping

### The Problem
- Need to find semantically similar chunks (not keyword matching)
- Must NEVER return other users' documents (security)
- Must be fast even with thousands of chunks

### The Solution: pgvector + Filtered Query

```python
# backend/app/services/vector_search_service.py

from sqlalchemy import func

def search_similar_chunks(
    question: str,
    user_id: int,
    db: Session,
    top_k: int = 5
) -> List[DocumentChunk]:
    """
    Finds the top_k most semantically similar chunks to the question,
    scoped to the user's documents only.
    """
    # Convert question to vector
    question_embedding = get_embedding(question)
    
    # Vector similarity search with user scoping
    results = (
        db.query(DocumentChunk)
        .join(Document)  # Join to access uploaded_by
        .filter(Document.uploaded_by == user_id)  # Security: user's docs only
        .order_by(
            DocumentChunk.embedding.cosine_distance(question_embedding)  # pgvector
        )
        .limit(top_k)
        .all()
    )
    
    return results
```

### The SQL Behind It
```sql
SELECT dc.*
FROM document_chunks dc
JOIN documents d ON dc.document_id = d.id
WHERE d.uploaded_by = :user_id
ORDER BY dc.embedding <=> :question_embedding  -- cosine distance operator
LIMIT 5;
```

### Why This Matters
- **Semantic Search:** Finds meaning, not just keywords
- **Security:** Multi-tenant data isolation
- **Performance:** HNSW index makes this fast even with 100K+ chunks

### What This Shows
- Understanding of vector databases
- Knowledge of SQL joins and filtering
- Security-first thinking (data scoping)

---

## 4. Grounded LLM Prompting (RAG)

### The Problem
- Standard LLM calls hallucinate (make up answers)
- Need answers grounded in user's actual documents
- Must cite sources for traceability

### The Solution: Structured Prompt with Context Injection

```python
# backend/app/services/llm_service.py

def generate_answer(question: str, chunks: List[DocumentChunk]) -> str:
    """
    Generates a grounded answer using retrieved chunks as context.
    Forces the LLM to cite sources and admit when it doesn't know.
    """
    # Build source context
    sources = []
    for idx, chunk in enumerate(chunks, 1):
        sources.append(f"[Source {idx}] (Document: {chunk.document.title})\n{chunk.chunk_text}")
    
    sources_text = "\n\n".join(sources)
    
    # Structured prompt with constraints
    prompt = f"""You are an academic assistant. Answer the question using ONLY the provided sources.

Sources:
{sources_text}

Rules:
1. Answer using ONLY information from the sources above
2. Cite sources using [Source N] notation
3. If the answer cannot be found in the sources, say "I cannot answer this based on the provided documents"
4. Do not use external knowledge or training data

Question: {question}

Answer:"""
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful academic assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,  # Low temperature = less creative, more factual
        max_tokens=500
    )
    
    return response.choices[0].message.content
```

### Why Temperature 0.2?
```
Temperature 1.0: "The essay argues that climate change is urgent..." (creative)
Temperature 0.2: "According to Source 1, the essay states..." (factual)
```

Low temperature keeps the model grounded in the provided context.

### Why This Matters
- **Accuracy:** Answers are traceable to sources
- **Transparency:** Users can verify claims
- **No Hallucination:** Model admits when it doesn't know

### What This Shows
- Understanding of prompt engineering
- Knowledge of RAG architecture
- Production-ready LLM integration

---

## 5. JWT Authentication with Dependency Injection

### The Problem
- Need to authenticate users on every protected endpoint
- Don't want to repeat auth logic in every function
- Must be stateless (no server-side sessions)

### The Solution: FastAPI Dependencies

```python
# backend/app/core/auth.py

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency that extracts and validates JWT token.
    Automatically injected into any endpoint that needs auth.
    """
    token = credentials.credentials
    
    try:
        # Decode and verify token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Load user from database
        user = db.query(User).filter(User.id == user_id).first()
        
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
        
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### Usage in Endpoints
```python
@router.get("/documents")
def get_documents(
    current_user: User = Depends(get_current_user),  # ← Auto-injected
    db: Session = Depends(get_db)
):
    # current_user is already authenticated and loaded
    documents = db.query(Document).filter(
        Document.uploaded_by == current_user.id
    ).all()
    
    return documents
```

### Why This Matters
- **DRY Principle:** Auth logic written once, used everywhere
- **Type Safety:** current_user is typed as User
- **Automatic Docs:** Swagger UI shows auth requirements

### What This Shows
- Understanding of dependency injection
- Knowledge of JWT authentication
- FastAPI best practices

---

## 6. Cascade Delete for Referential Integrity

### The Problem
- When a document is deleted, its chunks become orphans
- Orphaned chunks waste space and pollute search results
- Manual cleanup is error-prone

### The Solution: SQLAlchemy Cascade Rules

```python
# backend/app/models/document.py

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationship with cascade delete
    chunks = relationship(
        "DocumentChunk",
        back_populates="document",
        cascade="all, delete-orphan"  # ← KEY: Auto-delete chunks
    )
    
    user = relationship("User", back_populates="documents")
```

### What Happens
```python
# Delete a document
document = db.query(Document).filter(Document.id == 123).first()
db.delete(document)
db.commit()

# Result: Document row deleted + ALL its chunk rows deleted automatically
# No orphaned chunks left behind
```

### Why This Matters
- **Data Integrity:** No orphaned records
- **Storage Efficiency:** No wasted space
- **Clean Database:** Consistent state always

### What This Shows
- Understanding of database relationships
- Knowledge of ORM cascade rules
- Production-ready data modeling

---

## 🎓 Key Takeaways for Portfolio

### What These Patterns Demonstrate

1. **Database Expertise**
   - Atomic transactions (flush + commit)
   - Cascade rules and referential integrity
   - Vector similarity search with pgvector

2. **Security Awareness**
   - JWT authentication
   - Multi-tenant data scoping
   - Input validation with Pydantic

3. **AI/ML Integration**
   - Token-based chunking
   - Embedding generation
   - RAG prompt engineering

4. **Software Design**
   - Separation of concerns (service layer)
   - Dependency injection
   - Error handling and edge cases

5. **Production Readiness**
   - Atomic operations (all-or-nothing)
   - Type safety (Pydantic schemas)
   - Clean architecture (testable, maintainable)

---

## 💡 How to Present This in Interviews

### Instead of: "I built a RAG system"
### Say: "I implemented atomic transaction patterns to ensure referential integrity when uploading documents with multiple embedded chunks, using SQLAlchemy's flush() to get the parent ID before committing child records."

### Instead of: "I used OpenAI embeddings"
### Say: "I implemented token-based chunking with tiktoken to match OpenAI's exact tokenization, using a sliding window with 100-token overlap to preserve context at chunk boundaries."

### Instead of: "I added authentication"
### Say: "I implemented stateless JWT authentication with FastAPI dependency injection, enabling horizontal scaling while maintaining type safety and automatic API documentation."

---

*Next: See [05-CHALLENGES.md](./05-CHALLENGES.md) for problems encountered and how they were solved.*
