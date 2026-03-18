# Case Study: Building an Academic Assignment Helper with RAG Architecture

> This is a living document. It is updated at every meaningful step of the build.
> Its purpose is to serve as a portfolio case study that captures not just what was built,
> but why every decision was made — the thinking behind the code.

---

## Project Identity

**Project Name:** Academic Assignment Helper & Plagiarism Detector
**Type:** Backend REST API
**Stack:** FastAPI · PostgreSQL + pgvector · OpenAI · Docker · n8n
**Architecture Pattern:** RAG (Retrieval-Augmented Generation)
**Status:** In active development

---

## What This Project Is

This is a production-style REST API backend. There is no frontend, no UI.
It is a server that other applications talk to via HTTP requests — think of it
as the engine of a car. A frontend (web app, mobile app) could sit on top of it later,
but the engine is what makes everything work.

The system allows users to upload academic documents (essays, assignments, research papers),
and then ask natural language questions about them. The system finds the most relevant
parts of those documents and uses an LLM to generate a grounded, accurate answer — citing
exactly which document and section it drew from.

---

## The Core Problem It Solves

Standard LLM usage (just asking ChatGPT a question) has a fundamental limitation:
the model only knows what it was trained on. It has no access to your specific documents.

RAG solves this by adding a retrieval step before the LLM call:

```
Without RAG:   User question → LLM → answer (based on training data only)

With RAG:      User question → retrieve relevant chunks from YOUR documents
                             → LLM + retrieved context → grounded answer
```

The result is an answer that is accurate, specific to the user's actual content,
and traceable back to a source — not a hallucination.

---

## Why This Project Was Worth Building

This project sits at the intersection of four skills that are in high demand:

| Skill | How This Project Demonstrates It |
|-------|----------------------------------|
| Backend API design | FastAPI, REST endpoints, JWT authentication |
| Database engineering | PostgreSQL, pgvector, relational schema design |
| AI/ML integration | Embeddings, vector search, LLM prompting |
| DevOps fundamentals | Docker, Docker Compose, environment configuration |

Most junior developers can build a CRUD app. Far fewer can explain what RAG is,
why it matters, and show working production-style code for it.

---

## Architecture Overview

```
Client (HTTP)
     │
     ▼
FastAPI Backend
     │
     ├── Auth (JWT)
     ├── Assignments (CRUD)
     ├── Documents (upload + chunking + embedding)
     └── RAG Query (vector search + LLM answer)
     │
     ▼
PostgreSQL + pgvector
     │
     ├── users
     ├── assignments
     ├── documents
     └── document_chunks  ← where vector search happens
     │
     ▼
OpenAI API
     ├── text-embedding-3-small  (embedding generation)
     └── gpt-3.5-turbo           (answer generation)
```

---

## Milestone 1 — Foundation (Completed)

### What Was Built
- User registration and login with JWT authentication
- Full CRUD operations for assignments
- Basic document upload endpoint
- PostgreSQL database with pgvector extension
- Docker containerization of all services

### Key Technical Decisions

**JWT Authentication**
Chose stateless JWT tokens over session-based auth. Reason: REST APIs are stateless
by design. Sessions require server-side storage and don't scale horizontally.
JWT tokens carry the user identity inside the token itself — no database lookup needed
on every request.

**bcrypt for password hashing**
Industry standard for password storage. bcrypt is intentionally slow (configurable
cost factor), which makes brute-force attacks computationally expensive.
Never store plain text passwords — this is non-negotiable.

**PostgreSQL + pgvector over a dedicated vector database**
Could have used Pinecone, Weaviate, or Chroma as a dedicated vector store.
Chose pgvector because it runs as a PostgreSQL extension — no extra infrastructure,
no extra service to manage, no extra cost. For an MVP, keeping the stack simple
is the right call. pgvector is used in production by real companies.

---

## Milestone 2 — RAG Implementation (In Progress)

### The Problem With the Original Plan

The original design had one embedding per document stored directly on the `Document` model.
This was identified as architecturally wrong before implementation began.

**Why one embedding per document fails:**
When you generate one embedding for a 20-page document, you get a single vector that
represents the average meaning of the entire document. It's a blurry, imprecise
representation. When a user asks a specific question, the search compares their question
against that blurry average — and often fails to find the right content.

**The correct approach — chunking:**
Split each document into small overlapping chunks (~500 tokens each). Generate one
embedding per chunk. Store each chunk as its own database row. Now the search is
precise — it finds the exact paragraph that answers the question, not a blurry
average of the whole document.

```
Wrong:   Document (20 pages) → 1 embedding → imprecise search
Correct: Document (20 pages) → 40 chunks → 40 embeddings → precise search
```

### What a Token Is

A token is not a word. It is roughly 4 characters of English text.
"embedding" = 1 token. "unbelievable" = 2 tokens. A 500-word paragraph ≈ 375 tokens.
OpenAI's models have token limits — `text-embedding-3-small` accepts up to 8191 tokens.
We use `tiktoken` (OpenAI's own tokenizer) to count tokens so our counts match
exactly what OpenAI counts.

### What Chunk Overlap Is and Why It Matters

When splitting a document at a boundary, you risk cutting a sentence or idea in half.
The end of chunk 1 and the start of chunk 2 lose their connection.

Overlap means chunk 2 starts 100 tokens before where chunk 1 ended.
The boundary context is preserved in both chunks. No idea gets lost at the seams.

```
Chunk 1: [=============================[overlap]]
Chunk 2:                      [[overlap]=================================]
```

The overlap math: `next_start = current_start + CHUNK_SIZE - CHUNK_OVERLAP`
With chunk size 500 and overlap 100: next chunk starts at position 400, not 500.

### Security Decision — `uploaded_by` on Document

The original `Document` model had no link to the user who uploaded it.
This was a security vulnerability: a RAG query would search ALL documents from ALL users,
leaking other users' private academic content to whoever is asking.

Fix: added `uploaded_by` as a non-nullable foreign key to `users.id`.
Every document is owned by exactly one user. The RAG search filters by this field —
users only ever search their own documents.

This is called **data scoping** — a fundamental security pattern in multi-user systems.

### The `DocumentChunk` Model — Why a Separate Table

Chunks are not stored inside the `Document` row. They have their own table: `document_chunks`.

Reason: each chunk needs its own embedding (a 1536-dimensional vector). You cannot store
multiple vectors in one row cleanly. A separate table with a foreign key back to the
parent document is the correct relational design.

The relationship: one `Document` has many `DocumentChunks`.
The search queries `document_chunks` — the `documents` table is just the container.

**`cascade="all, delete-orphan"`** on the relationship means: if a document is deleted,
all its chunks are automatically deleted too. Without this, orphaned chunk rows would
accumulate in the database forever — wasting space and polluting search results.
This is called referential integrity.

### The Separation of Concerns Principle in Practice

Each service in this project has one job and knows nothing about the others:

```
chunking_service.py    → text in, list of chunk strings out
embedding_service.py   → text in, list of 1536 floats out
vector_search_service  → question in, relevant chunks out  (coming next)
```

The upload endpoint doesn't know how embeddings are generated.
It just calls the service and gets a vector back.
If OpenAI is swapped for a local model tomorrow, only `embedding_service.py` changes.
Nothing else in the codebase breaks.

This is the single responsibility principle — one of the most important design
principles in software engineering.

### Why Error Handling in the Embedding Service Matters

The embedding service makes a network call to an external API. That means it can fail:
- Bad API key → `AuthenticationError`
- Too many requests → `RateLimitError`
- No internet → `APIConnectionError`

Each failure has a different cause and a different fix. Catching them all as one
generic `Exception` and saying "something went wrong" is useless to whoever is
debugging at 2am. Specific exceptions with specific messages is professional practice.

The service also checks the API key before making the call — a fast-fail pattern that avoids a wasted network round-trip when the configuration is obviously wrong.

---

## Step 4 — Wiring the Upload Endpoint (Completed)

### What Was Built
- The `/documents/upload` endpoint now chunks the uploaded text and generates an embedding for each chunk
- All `DocumentChunk` rows are persisted in a single transaction with the parent `Document`
- All document endpoints (`GET /`, `GET /:id`, `DELETE /:id`) are now scoped to the authenticated user
- The response schema exposes `uploaded_by` and a computed `chunk_count`

### The `db.flush()` Pattern

The upload endpoint needs the `Document.id` before the transaction is committed — because each `DocumentChunk` row needs `document_id` as a foreign key.

`db.flush()` sends the INSERT to the database and makes the auto-generated `id` available in Python, but does not commit. The entire operation — document row + all chunk rows — is committed together at the end. If embedding generation fails halfway through, nothing is written. The database stays clean.

This is called an **atomic transaction**: all-or-nothing. Either the document and all its chunks are saved, or none of them are.

```
db.add(document)
db.flush()          ← id is now available, transaction still open
for chunk in chunks:
    db.add(DocumentChunk(document_id=document.id, ...))
db.commit()         ← everything lands at once
```

### Why All Endpoints Got Auth

The GET and DELETE endpoints previously had no authentication. That meant any unauthenticated caller could list or delete any document in the system.

Adding `current_user = Depends(get_current_user)` to every endpoint and filtering all queries by `uploaded_by == current_user.id` closes this. A user can only see and delete their own documents. This is the same data scoping principle applied consistently across the entire resource.

### The Flow End-to-End

```
POST /documents/upload
  │
  ├── JWT verified → current_user resolved
  ├── file.read() → raw text
  ├── Document row created, db.flush() → document.id available
  ├── chunk_text(content) → [chunk_0, chunk_1, ..., chunk_n]
  ├── for each chunk: get_embedding(chunk) → [1536 floats]
  ├── DocumentChunk row created per chunk
  └── db.commit() → everything persisted atomically
```

This is the first moment in the project where all three layers — the API, the services, and the database — work together as one system.

---

## Step 5 — RAG Query Endpoint (Completed)

### What Was Built
- `vector_search_service.py` — embeds the question and retrieves the top 5 most similar chunks from `document_chunks`, scoped to the current user
- `llm_service.py` — builds a grounded prompt from retrieved chunks and calls GPT-3.5-turbo to generate an answer with source citations
- `api/query.py` — single `POST /query` endpoint that wires both services together
- `schemas/query.py` — typed request/response shapes

### How the Vector Search Works

pgvector exposes a cosine distance operator (`<=>`). The query sorts all chunks belonging to the user's documents by how close their embedding is to the question's embedding, and takes the top 5.

```
question → get_embedding() → [1536 floats]
         → ORDER BY chunk.embedding <=> question_embedding
         → LIMIT 5
         → top 5 most semantically similar chunks
```

Cosine distance measures the angle between two vectors. A distance of 0 means identical meaning. A distance of 1 means completely unrelated. The closest chunks are the most relevant to the question.

The query is also filtered by `Document.uploaded_by == user_id` — the same data scoping pattern applied in Step 4. The vector search only ever touches the current user's documents.

### Why Temperature 0.2 on the LLM Call

Temperature controls how creative (random) the model's output is. A temperature of 1.0 means the model freely picks from many possible next tokens — good for creative writing, bad for factual Q&A. A temperature of 0.2 keeps the model close to the most probable tokens — it stays grounded in the context it was given and is less likely to hallucinate.

For a system where accuracy and traceability matter, low temperature is the right call.

### The Prompt Design

The prompt does three things:
1. Constrains the model — "answer using ONLY the provided sources"
2. Requires citation — "cite the source number when you use information from it"
3. Handles the no-answer case — "if the answer cannot be found in the sources, say so explicitly"

Without constraint 1, the model will blend its training data with the retrieved context and you lose the grounding that makes RAG valuable. Without constraint 3, the model will hallucinate an answer rather than admit it doesn't know.

### The Full RAG Flow End-to-End

```
POST /query  { "question": "What is the main argument of this essay?" }
  │
  ├── JWT verified → current_user resolved
  ├── get_embedding(question) → [1536 floats]
  ├── SELECT chunks ORDER BY embedding <=> question_embedding
  │   WHERE document.uploaded_by = user_id LIMIT 5
  ├── Build prompt: system instruction + source blocks + question
  ├── GPT-3.5-turbo → grounded answer with [Source N] citations
  └── Return: { answer, source_document_ids, chunks_used }
```

This is the complete RAG loop. The system no longer answers from training data alone — every answer is grounded in the user's actual uploaded documents.

---

## Decisions Log

A running record of every meaningful technical decision made during the build.

| Decision | What Was Chosen | Why |
|----------|----------------|-----|
| Auth strategy | JWT (stateless) | REST APIs are stateless; no server-side session storage needed |
| Password hashing | bcrypt | Industry standard; intentionally slow to resist brute force |
| Vector storage | pgvector (PostgreSQL extension) | No extra infrastructure; production-ready; keeps stack simple |
| Embedding model | text-embedding-3-small | 1536 dims, cost-effective, high quality |
| LLM | gpt-3.5-turbo | Fast, affordable, sufficient for MVP |
| Chunk size | 500 tokens | Balances context richness vs. retrieval precision |
| Chunk overlap | 100 tokens | Prevents meaning loss at chunk boundaries |
| Chunking strategy | Token-based (tiktoken) | Matches OpenAI's own tokenizer exactly |
| Document ownership | uploaded_by FK (non-nullable) | Security — scopes search results per user |
| Chunk storage | Separate table (document_chunks) | Each chunk needs its own embedding; clean relational design |
| Cascade delete | all, delete-orphan on chunks | Referential integrity — no orphaned rows on document deletion |

---

## Concepts Glossary

**RAG (Retrieval-Augmented Generation)**
A pattern where relevant context is retrieved from a database before an LLM generates
an answer. The LLM uses the retrieved context to produce a grounded, accurate response
rather than relying solely on its training data.

**Embedding**
A numerical representation of text as a vector (list of floats). Texts with similar
meaning produce vectors that are close together in vector space. This is what enables
semantic search — finding documents by meaning, not just keyword matching.

**Vector Search / Cosine Similarity**
A method of finding the most similar vectors in a database. Cosine similarity measures
the angle between two vectors — the smaller the angle, the more similar the meaning.
pgvector uses the `<=>` operator for this.

**Token**
The unit of text that LLMs process. Roughly 4 characters of English text.
Not the same as a word. Models have token limits for both input and output.

**Chunking**
Splitting a large document into smaller pieces before embedding. Each chunk gets its
own embedding, enabling precise retrieval of specific sections rather than blurry
whole-document averages.

**Chunk Overlap**
A technique where consecutive chunks share some tokens at their boundaries.
Prevents meaning from being lost when a sentence or idea spans a chunk boundary.

**Separation of Concerns**
A design principle where each module or function has one clearly defined responsibility.
Makes code easier to test, maintain, and swap out without breaking other parts.

**Referential Integrity**
The guarantee that relationships between database tables remain consistent.
A foreign key with cascade delete ensures child rows are removed when the parent is deleted.

**Data Scoping**
Filtering database queries to only return data belonging to the authenticated user.
A fundamental security pattern in any multi-user system.

---

## What This Project Demonstrates to a Hiring Manager

1. You understand AI/ML integration beyond just calling an API — you built the retrieval layer
2. You make deliberate architectural decisions and can explain the reasoning behind them
3. You think about security (data scoping, auth, non-nullable ownership fields)
4. You understand database design (relational schema, foreign keys, cascade rules)
5. You write code that is maintainable (separation of concerns, single responsibility)
6. You build incrementally with clean git history and conventional commits

---

*Last updated: Milestone 2, Step 3 complete*
*Next: Step 4 — Update document upload to wire chunking and embedding into the pipeline*
