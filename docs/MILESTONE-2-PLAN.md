# Milestone 2: RAG Implementation Plan (Revised)

## 🎯 Objective
Implement core RAG (Retrieval-Augmented Generation) functionality — semantic document search
and AI-powered Q&A over uploaded academic documents.

---

## 📋 Current State

### ✅ What We Have
- User auth with JWT tokens
- Assignment CRUD operations
- Basic document upload endpoint (saves file content, nothing more)
- PostgreSQL + pgvector extension ready
- `Document` model with an `embedding` column (Vector 1536) — but it's never populated
- Docker containerization

### ❌ What's Missing (and Why It Matters)
| Gap | Why It Blocks Us |
|-----|-----------------|
| No embedding generation | Can't do vector search without embeddings |
| No chunking | One embedding per whole document = poor retrieval accuracy |
| No `DocumentChunk` model | Chunks need their own DB rows and embeddings |
| No `user_id` on `Document` | RAG search has no way to scope results to the right user |
| No vector search service | Can't retrieve relevant context for RAG |
| No RAG query endpoint | The actual product feature doesn't exist yet |
| RAG router not registered in `main.py` | Easy to forget, breaks everything if missed |

---

## ⚠️ Corrections to the Original Plan

### Correction 1: Chunking is NOT optional
The original plan listed chunking as "Step 5 - Optional Enhancement". This was wrong.

Here's why it matters: when you upload a 10-page document, the current approach generates
ONE embedding for the entire document. That single embedding is an average of all the meaning
in the document — it becomes a blurry, imprecise representation. When you later search for
something specific that appears on page 7, the system won't find it reliably.

The correct approach: split the document into small overlapping chunks (e.g. 500 tokens each),
generate one embedding per chunk, and store each chunk as its own row. Now your search is
precise — it finds the exact paragraph that answers the question.

Chunking moves to Step 2, right after the embedding service.

### Correction 2: `Document` model is missing `user_id`
The current `Document` model has no link to the user who uploaded it. This creates two problems:

- Security: a RAG query would search ALL documents from ALL users, leaking other users' data
- Correctness: results would be polluted with irrelevant documents from other users

Fix: add `uploaded_by` (ForeignKey to `users.id`) to the `Document` model before we go further.

### Correction 3: `DocumentChunk` model doesn't exist yet
The plan mentioned chunking but never addressed where chunks are stored. Chunks are NOT stored
inside the `Document` row. They need their own table: `document_chunks`, with columns for the
chunk text, its embedding, its position in the document, and a foreign key back to the parent
`Document`. This model needs to be created as part of Step 3.

### Correction 4: RAG router must be registered in `main.py`
When we create `backend/app/api/rag.py`, it won't do anything until it's imported and registered
in `main.py` the same way `auth`, `assignments`, and `documents` routers are. This is a small
but critical step that's easy to forget and will cause a silent failure (endpoint simply won't exist).

---

## 🚀 Revised Implementation Steps

### Step 1 — Embedding Service
**What:** A Python service that takes a string of text and returns a 1536-dimensional vector.

**File to create:** `backend/app/services/embedding_service.py`

**How it works:**
- Calls OpenAI's `text-embedding-3-small` model
- Returns a list of 1536 floats representing the semantic meaning of the text
- Handles missing API key gracefully (raises a clear error, doesn't silently fail)

**Why first:** Every other step depends on this. You can't embed chunks, search vectors,
or answer questions without it. It's also the smallest and most isolated piece — easy to
test independently.

**New dependency:** `openai==1.12.0` → add to `requirements.txt`

---

### Step 2 — Chunking Service
**What:** A service that splits a long document into smaller, overlapping text chunks.

**File to create:** `backend/app/services/chunking_service.py`

**How it works:**
- Takes raw document text as input
- Splits it into chunks of ~500 tokens
- Each chunk overlaps the previous by ~100 tokens (so context isn't lost at boundaries)
- Returns a list of strings (the chunks)

**Why second:** The embedding service needs something to embed. Feeding it whole documents
is the wrong approach. Chunking must come before embedding in the pipeline.

**New dependency:** `tiktoken==0.5.2` → add to `requirements.txt` (used for accurate token counting)

---

### Step 3 — Database: Add `user_id` to `Document` + Create `DocumentChunk` model
**What:** Two database changes before we touch any upload logic.

**File to modify:** `backend/models.py`

**Change 1 — Add `uploaded_by` to `Document`:**
```
uploaded_by = Column(Integer, ForeignKey("users.id"))
```
This links every document to the user who uploaded it. Required for scoped RAG search.

**Change 2 — Add `DocumentChunk` model:**
```
class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    id, chunk_text, chunk_index, embedding (Vector 1536), document_id (FK)
```
Each row is one chunk of a parent document, with its own embedding. This is what the
vector search will actually query — not the `documents` table.

**Why before upload changes:** If we update the upload endpoint before the model exists,
the code will crash. Schema first, then logic.

---

### Step 4 — Update Document Upload
**What:** Wire the chunking and embedding services into the existing upload endpoint.

**File to modify:** `backend/app/api/documents.py`

**New flow:**
1. Receive uploaded file
2. Save the `Document` row (with `uploaded_by` from the authenticated user)
3. Pass document content to chunking service → get list of chunks
4. For each chunk: call embedding service → get vector
5. Save each chunk as a `DocumentChunk` row with its embedding
6. Return the document response

**Why this order matters:** The document must be saved first (to get its `id`),
then chunks are saved with that `document_id` as a foreign key.

---

### Step 5 — Vector Search Service
**What:** A service that takes a question, embeds it, and finds the most semantically
similar chunks in the database.

**File to create:** `backend/app/services/vector_search_service.py`

**How it works:**
- Embeds the query text using the embedding service
- Runs a pgvector cosine similarity query against `document_chunks`
- Filters by `uploaded_by` (scoped to the requesting user)
- Returns the top-k most relevant chunks with their similarity scores

**The core SQL it uses:**
```sql
SELECT chunk_text, document_id,
       1 - (embedding <=> :query_vector) AS similarity
FROM document_chunks
WHERE document_id IN (
    SELECT id FROM documents WHERE uploaded_by = :user_id
)
ORDER BY embedding <=> :query_vector
LIMIT :k;
```

---

### Step 6 — RAG Query Endpoint + Register Router
**What:** The actual product feature — an endpoint that answers questions using
the user's uploaded documents as context.

**Files to create:**
- `backend/app/api/rag.py`
- `backend/app/schemas/rag.py`

**File to modify:** `backend/main.py` (register the router)

**Endpoint:** `POST /rag/query`

**Request:**
```json
{
  "question": "What is the main argument in the uploaded essay?",
  "assignment_id": 1,
  "top_k": 3
}
```

**Response:**
```json
{
  "answer": "The main argument is...",
  "sources": [
    {"document_id": 1, "filename": "essay.txt", "chunk_index": 3, "relevance": 0.91}
  ]
}
```

**Internal flow:**
1. Get authenticated user from JWT
2. Embed the question
3. Run vector search (scoped to user's documents)
4. Build a prompt: system context + retrieved chunks + user question
5. Call OpenAI `gpt-3.5-turbo` with the prompt
6. Return the answer and the source chunks it was based on

---

## 🔧 Technical Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| Embedding model | `text-embedding-3-small` | 1536 dims, cheap, high quality |
| LLM | `gpt-3.5-turbo` | Fast, affordable, good enough for MVP |
| Vector search | pgvector cosine similarity | Already in our DB, no extra infra |
| Chunk size | ~500 tokens | Balances context richness vs. precision |
| Chunk overlap | ~100 tokens | Prevents losing meaning at chunk boundaries |

---

## 📦 Dependencies to Add

```
openai==1.12.0
tiktoken==0.5.2
```

---

## 🧪 How We'll Test Each Step

| Step | How to Verify |
|------|--------------|
| Embedding service | Call it with a string, assert you get a list of 1536 floats |
| Chunking service | Feed it a long text, assert chunks are correct size with overlap |
| DB model changes | Run the app, check tables exist in PostgreSQL |
| Updated upload | Upload a file, query `document_chunks` table, confirm rows exist |
| Vector search | Search for something you know is in a document, confirm it's returned |
| RAG endpoint | Ask a question about an uploaded document, confirm a grounded answer |

---

## ✅ Milestone 2 Complete When

- Documents are chunked and each chunk has an embedding stored in `document_chunks`
- Vector search returns the correct chunks for a given question
- RAG endpoint returns an answer grounded in the user's own documents
- Results are scoped per user (no cross-user data leakage)
- RAG router is registered and visible in `/docs`

---

## 📝 Engineering Notes

- Never commit the OpenAI API key — it lives in `.env` only
- `uploaded_by` on `Document` must be populated from the JWT token, not from the request body
- Chunk overlap is important — don't skip it to save time
- The `document_chunks` table is what gets searched, not `documents`
- Register the RAG router in `main.py` — don't forget this step

---

## 🔄 Post-Milestone 2 (Future Work)

- Plagiarism detection: compare document embeddings for similarity scores
- Batch document processing via n8n workflows
- Caching embeddings for repeated queries
- Support for PDF/DOCX parsing (currently only plain text)
