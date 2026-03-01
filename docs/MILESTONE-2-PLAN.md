# Milestone 2: RAG Implementation Plan

## 🎯 Objective
Implement core RAG (Retrieval-Augmented Generation) functionality to enable semantic search and AI-powered document analysis.

---

## 📋 Current State Assessment

### ✅ What We Have
- User authentication & JWT tokens
- Assignment CRUD operations
- Document upload endpoint (basic)
- PostgreSQL with pgvector extension
- Document model with `embedding` field (Vector 1536)
- Docker containerization

### ❌ What's Missing
- No embedding generation for documents
- No vector similarity search
- No RAG query endpoint
- No AI/LLM integration for answer generation
- No chunking strategy for large documents

---

## 🚀 Implementation Steps

### **Step 1: Embedding Service** (PRIORITY)
**Goal:** Generate vector embeddings from document text

**Files to Create:**
- `backend/app/services/embedding_service.py`

**What It Does:**
- Accepts text input
- Generates 1536-dimensional embeddings using OpenAI API
- Handles errors and rate limiting
- Provides fallback for missing API keys (development mode)

**Dependencies Needed:**
- `openai` package (add to requirements.txt)

**Why This First:**
- Foundation for all RAG functionality
- Self-contained and testable
- Unblocks vector search implementation

---

### **Step 2: Update Document Upload**
**Goal:** Auto-generate embeddings when documents are uploaded

**Files to Modify:**
- `backend/app/api/documents.py`

**Changes:**
- Import embedding service
- Call embedding generation after document upload
- Store embedding in database
- Handle embedding failures gracefully

**Testing:**
- Upload a document via API
- Verify embedding is stored in database
- Check embedding dimensions (should be 1536)

---

### **Step 3: Vector Search Service**
**Goal:** Implement semantic similarity search

**Files to Create:**
- `backend/app/services/vector_search_service.py`

**What It Does:**
- Accept query text
- Generate query embedding
- Perform cosine similarity search using pgvector
- Return top-k most relevant documents
- Include relevance scores

**Database Query:**
```sql
SELECT id, filename, content, 
       1 - (embedding <=> query_embedding) as similarity
FROM documents
ORDER BY embedding <=> query_embedding
LIMIT k;
```

---

### **Step 4: RAG Query Endpoint**
**Goal:** Create endpoint for AI-powered question answering

**Files to Create:**
- `backend/app/api/rag.py`
- `backend/app/schemas/rag.py`

**Endpoint Design:**
```
POST /rag/query
{
  "question": "What is the main topic of assignment X?",
  "assignment_id": 1,  // optional filter
  "top_k": 3           // number of documents to retrieve
}

Response:
{
  "answer": "The main topic is...",
  "sources": [
    {"document_id": 1, "filename": "doc.txt", "relevance": 0.89},
    ...
  ],
  "confidence": 0.85
}
```

**Flow:**
1. Receive user question
2. Generate question embedding
3. Search for relevant documents (vector search)
4. Construct prompt with retrieved context
5. Call LLM (OpenAI) for answer generation
6. Return answer with sources

---

### **Step 5: Document Chunking (Optional Enhancement)**
**Goal:** Handle large documents by splitting into chunks

**Files to Create:**
- `backend/app/services/chunking_service.py`

**Strategy:**
- Split documents into 500-1000 token chunks
- Maintain overlap between chunks (100 tokens)
- Store chunks as separate embeddings
- Link chunks to parent document

**Why Optional:**
- Not critical for MVP
- Can be added after basic RAG works
- Improves accuracy for large documents

---

## 🔧 Technical Decisions

### Embedding Model
**Choice:** OpenAI `text-embedding-3-small` (1536 dimensions)
- **Pros:** High quality, fast, cost-effective
- **Cons:** Requires API key, external dependency
- **Alternative:** Local model (sentence-transformers) for development

### LLM for Answer Generation
**Choice:** OpenAI `gpt-3.5-turbo`
- **Pros:** Fast, affordable, good quality
- **Cons:** Requires API key
- **Alternative:** `gpt-4` for higher quality (more expensive)

### Vector Search Strategy
**Choice:** pgvector cosine similarity (`<=>` operator)
- **Pros:** Built into PostgreSQL, no extra infrastructure
- **Cons:** Not as fast as dedicated vector DBs (acceptable for MVP)

---

## 📦 New Dependencies

Add to `requirements.txt`:
```
openai==1.12.0
tiktoken==0.5.2  # for token counting
```

---

## 🧪 Testing Strategy

### Unit Tests
- `test_embedding_service.py`: Test embedding generation
- `test_vector_search.py`: Test similarity search
- `test_rag_query.py`: Test end-to-end RAG flow

### Integration Tests
1. Upload document → verify embedding stored
2. Query with known answer → verify correct retrieval
3. Test with multiple documents → verify ranking

### Manual Testing
1. Upload sample academic documents
2. Ask questions about the content
3. Verify answers are accurate and cite sources

---

## 🎯 Success Criteria

**Milestone 2 Complete When:**
- ✅ Documents automatically get embeddings on upload
- ✅ Vector search returns relevant documents
- ✅ RAG endpoint answers questions using document context
- ✅ Sources are cited in responses
- ✅ All tests pass
- ✅ API documentation updated

---

## 📊 Estimated Effort

| Step | Complexity | Time Estimate |
|------|-----------|---------------|
| Step 1: Embedding Service | Low | 30 min |
| Step 2: Update Upload | Low | 20 min |
| Step 3: Vector Search | Medium | 45 min |
| Step 4: RAG Endpoint | Medium | 1 hour |
| Step 5: Chunking (Optional) | Medium | 1 hour |
| Testing & Documentation | Low | 30 min |
| **Total** | | **~3-4 hours** |

---

## 🚦 Next Immediate Action

**START HERE:** Implement Step 1 - Embedding Service

This is the smallest, most foundational piece that unblocks everything else.

---

## 📝 Notes

- Keep OpenAI API key in `.env` file (never commit)
- Add error handling for API failures
- Consider rate limiting for production
- Monitor embedding costs (very low for MVP)
- Document all API endpoints in Swagger

---

## 🔄 Future Enhancements (Post-Milestone 2)

- Plagiarism detection using document similarity
- Multi-language support
- Custom fine-tuned embeddings
- Caching for frequently asked questions
- Batch processing for multiple documents
- Real-time document analysis via n8n workflows
