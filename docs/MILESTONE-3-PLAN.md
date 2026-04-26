# Milestone 3: Plagiarism Detection

## Objective
Build a two-layer plagiarism detection system on top of the RAG infrastructure already in place.
Layer 1 catches exact copies instantly using SHA-256 hashing. Layer 2 catches paraphrasing using
the embeddings already stored in pgvector. No new AI infrastructure needed — we reuse everything
built in Milestone 2.

---

## Current State Coming Into This Milestone

### What Milestone 2 Left Us
- Documents are uploaded, chunked, and embedded — each chunk has a vector in `document_chunks`
- `content_hash` column exists on `Document` and is populated with SHA-256 on every upload
- Vector search is working via pgvector cosine distance
- RAG query endpoint is live at `POST /query/`
- All results are scoped per user (no cross-user data leakage)

### What's Missing
| Gap | Why It Matters |
|-----|---------------|
| No duplicate hash check on upload | Exact copies go undetected |
| No similarity check on upload | Paraphrased submissions go undetected |
| No plagiarism result returned to the caller | Upload endpoint gives no signal about duplicates |
| No dedicated plagiarism endpoint | No way to check a document after the fact |
| `DocumentSchema` doesn't expose `content_hash` | API response hides the fingerprint |

---

## What We Are NOT Doing in This Milestone
- No UI — detection results are returned in the API response only
- No cross-user plagiarism detection — we scope to the current user's documents only
- No PDF/DOCX parsing — plain text only, same as Milestone 2
- No n8n workflow integration yet — that comes later

---

## Implementation Steps

### Step 1 — Hash-Based Duplicate Detection (already partially done)
**Status:** `content_hash` is stored. The check itself is not implemented yet.

**What:** On upload, before saving the new document, query the DB for any existing document
owned by the same user with the same `content_hash`. If found, return a 409 response
with the ID of the matching document.

**File to modify:** `backend/app/api/documents.py`

**Why first:** It's the cheapest check possible — one indexed DB lookup, no AI calls.
Always run the cheap check before the expensive one.

**Response when duplicate found:**
```json
{
  "detail": "Exact duplicate detected.",
  "matched_document_id": 12
}
```

---

### Step 2 — Vector Similarity Plagiarism Check
**What:** After chunking and embedding the new document, compare its chunk embeddings
against existing chunks in the DB (scoped to the same user). If the average cosine
similarity across the top matches exceeds a threshold (e.g. 0.92), flag it as a
likely paraphrase.

**File to create:** `backend/app/services/plagiarism_service.py`

**Why a separate service:** The upload endpoint is already doing 3 things (save, chunk, embed).
Plagiarism logic belongs in its own service — easier to test, easier to tune the threshold later.

**How it works:**
1. Take the list of chunk embeddings from the newly uploaded document
2. For each chunk, find the closest existing chunk in the DB using cosine distance
3. Average the top similarity scores
4. If average similarity > threshold → flag as potential plagiarism

**Returns:**
```python
{
    "is_flagged": True,
    "similarity_score": 0.95,       # 0.0 to 1.0
    "matched_document_id": 7,       # the most similar existing document
    "detection_method": "vector"    # "hash" or "vector"
}
```

---

### Step 3 — Wire Detection Into Upload Response
**What:** Update the upload endpoint to run both checks and include the plagiarism
result in the response without blocking the upload (we flag, we don't reject, for
vector similarity — only exact hash match is a hard reject).

**File to modify:** `backend/app/api/documents.py`

**Updated upload flow:**
```
1. Read file content
2. Compute SHA-256 hash
3. Check for exact hash match → if found, return 409 immediately
4. Save Document row
5. Chunk + embed content
6. Save DocumentChunk rows
7. Run vector similarity check against existing chunks
8. Return document + plagiarism_result in response
```

**Why hash check is a hard reject but vector is not:**
Hash match means byte-for-byte identical — there is no ambiguity. Vector similarity
is probabilistic — a 0.93 score is suspicious but not proof. We flag it and let a
human decide.

---

### Step 4 — Dedicated Plagiarism Check Endpoint
**What:** A standalone endpoint to check an already-uploaded document for plagiarism
after the fact. Useful for re-checking documents uploaded before this feature existed
(they have no hash, their similarity was never checked).

**File to create:** `backend/app/api/plagiarism.py`

**Endpoint:** `POST /plagiarism/check/{document_id}`

**Response:**
```json
{
  "document_id": 5,
  "filename": "essay.txt",
  "hash_check": {
    "is_duplicate": false
  },
  "vector_check": {
    "is_flagged": true,
    "similarity_score": 0.94,
    "matched_document_id": 3
  }
}
```

**File to modify:** `backend/main.py` — register the new router

---

### Step 5 — Expose `content_hash` in API Response
**What:** Update `DocumentSchema` so `content_hash` is visible in the API response.
Right now it's stored in the DB but hidden from callers.

**File to modify:** `backend/app/schemas/document.py`

**Why:** Clients (and future n8n workflows) need to see the hash to build their own
duplicate detection logic on top of the API.

---

## Technical Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| Hash check result | Hard 409 reject | No ambiguity — identical bytes = duplicate |
| Vector check result | Soft flag in response | Similarity is probabilistic, not proof |
| Similarity threshold | 0.92 | Tunable constant, high enough to avoid false positives |
| Scope | Per-user only | Consistent with RAG scoping, avoids privacy issues |
| Detection in upload | Both checks run on every upload | No extra endpoint needed for new documents |

---

## Files Changed in This Milestone

| File | Change |
|------|--------|
| `backend/app/api/documents.py` | Add hash check + wire plagiarism result into response |
| `backend/app/services/plagiarism_service.py` | New — vector similarity detection logic |
| `backend/app/api/plagiarism.py` | New — standalone check endpoint |
| `backend/app/schemas/document.py` | Expose `content_hash` in response schema |
| `backend/main.py` | Register plagiarism router |

---

## Milestone 3 Complete When

- Uploading an exact duplicate returns a 409 with the matched document ID
- Uploading a paraphrased document returns a flagged response with a similarity score
- `POST /plagiarism/check/{document_id}` works for documents uploaded before this feature
- `content_hash` is visible in the document API response
- All checks are scoped to the authenticated user's documents only

---

## Engineering Notes

- Always run the hash check before the vector check — hash is free, vector costs DB compute
- The similarity threshold (0.92) is a constant — define it in `plagiarism_service.py` so it's
  easy to tune without touching endpoint logic
- Documents uploaded before Milestone 3 will have `content_hash` populated (we added that in
  Step 2 of this milestone's predecessor) but were never checked — the dedicated endpoint
  in Step 4 handles that backfill use case
- Never compare across users — always filter by `uploaded_by = current_user.id`

---

## Post-Milestone 3 (Future Work)

- Backfill `content_hash` for any documents uploaded before Step 1-2 of plagiarism work
- n8n workflow: trigger plagiarism check automatically when a document is uploaded via workflow
- Cross-assignment detection (same user, different assignments)
- Admin view: flag documents for instructor review
- Support PDF/DOCX parsing so plagiarism detection works beyond plain text
