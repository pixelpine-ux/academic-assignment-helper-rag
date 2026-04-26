# File Upload API Documentation

## Overview
The document upload endpoint accepts PDF, DOCX, and TXT files, validates them, extracts text content, and processes them through the RAG pipeline (chunking → embedding → storage).

## Endpoint

```
POST /documents/upload
```

## Authentication
Requires JWT token in Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Request

### Headers
- `Authorization: Bearer <token>` (required)
- `Content-Type: multipart/form-data` (automatic)

### Body (multipart/form-data)
- `file` (required): The document file to upload
- `assignment_id` (optional): Integer ID to associate document with an assignment

### Example with cURL
```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "file=@/path/to/document.pdf" \
  -F "assignment_id=1"
```

### Example with Python
```python
import requests

url = "http://localhost:8000/documents/upload"
headers = {"Authorization": "Bearer YOUR_TOKEN_HERE"}
files = {"file": open("document.pdf", "rb")}
data = {"assignment_id": 1}

response = requests.post(url, headers=headers, files=files, data=data)
print(response.json())
```

## Supported File Formats

| Format | Extension | Parser | Notes |
|--------|-----------|--------|-------|
| PDF | `.pdf` | PyPDF2 | Extracts text from all pages |
| Word Document | `.docx` | python-docx | Extracts paragraphs |
| Text File | `.txt` | Native | UTF-8 with Latin-1 fallback |

## File Validation Rules

### ✅ Valid Files
- Extension: `.pdf`, `.docx`, or `.txt`
- Size: 1 byte to 10MB
- Content: Must contain extractable text

### ❌ Invalid Files (HTTP 400)
- **Unsupported extension**: `.exe`, `.zip`, `.jpg`, etc.
  ```json
  {
    "detail": "Unsupported file type: .exe. Allowed types: .pdf, .docx, .txt"
  }
  ```

- **File too large**: > 10MB
  ```json
  {
    "detail": "File too large: 15.23MB. Maximum allowed: 10MB"
  }
  ```

- **Empty file**: 0 bytes
  ```json
  {
    "detail": "File is empty"
  }
  ```

- **Parsing failure**: Corrupted or unreadable file
  ```json
  {
    "detail": "Failed to parse .pdf file: Invalid PDF structure"
  }
  ```

- **No extractable text**: PDF with only images
  ```json
  {
    "detail": "PDF contains no extractable text"
  }
  ```

## Response

### Success (HTTP 200)
```json
{
  "id": 42,
  "filename": "research_paper.pdf",
  "content": "Full extracted text content...",
  "content_hash": "a3f5b8c9d2e1f4a7b6c5d8e9f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0",
  "uploaded_by": 1,
  "assignment_id": 1,
  "doc_metadata": {
    "size": 245678,
    "content_type": "application/pdf"
  },
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Error Responses

| Status Code | Meaning | Example |
|-------------|---------|---------|
| 400 | Bad Request | Invalid file type, too large, empty, or parsing failed |
| 401 | Unauthorized | Missing or invalid JWT token |
| 422 | Unprocessable Entity | Missing required fields |
| 500 | Internal Server Error | Database or OpenAI API failure |

## Processing Pipeline

After successful upload, the document goes through:

1. **Validation** (file_validator.py)
   - Check extension
   - Check file size
   - Reject if invalid

2. **Text Extraction** (file_parser_service.py)
   - Route to appropriate parser (PDF/DOCX/TXT)
   - Extract plain text
   - Handle encoding issues

3. **Chunking** (chunking_service.py)
   - Split text into 500-token chunks
   - 100-token overlap between chunks
   - Preserve context at boundaries

4. **Embedding** (embedding_service.py)
   - Convert each chunk to 1536-dim vector
   - Use OpenAI text-embedding-3-small
   - Store in database with chunk text

5. **Storage** (PostgreSQL + pgvector)
   - Save document record
   - Save N chunk records with embeddings
   - Create HNSW index for fast search

## Performance Considerations

### Upload Time Estimates
- **Small file** (< 1MB, ~10 chunks): 2-5 seconds
- **Medium file** (1-5MB, ~50 chunks): 10-30 seconds
- **Large file** (5-10MB, ~100 chunks): 30-60 seconds

Time depends on:
- File size
- Number of chunks generated
- OpenAI API latency
- Network speed

### Cost Estimates (OpenAI)
- **Embedding cost**: $0.02 per 1M tokens
- **Average document**: 10,000 tokens = $0.0002
- **Large document**: 50,000 tokens = $0.001

## Best Practices

### For Users
1. **Use text-based PDFs**: Scanned PDFs (images) won't work without OCR
2. **Keep files under 5MB**: Faster processing, lower costs
3. **Use descriptive filenames**: Helps with organization
4. **Check file content**: Ensure text is extractable before uploading

### For Developers
1. **Add progress indicators**: Long uploads need user feedback
2. **Implement async processing**: Move to background jobs for large files
3. **Add retry logic**: Handle transient OpenAI API failures
4. **Cache embeddings**: Avoid re-embedding identical content
5. **Monitor costs**: Track OpenAI API usage per user

## Troubleshooting

### "Unsupported file type" Error
- **Cause**: File extension not in allowed list
- **Solution**: Convert to PDF, DOCX, or TXT

### "File too large" Error
- **Cause**: File exceeds 10MB limit
- **Solution**: Split document or compress PDF

### "PDF contains no extractable text" Error
- **Cause**: PDF is scanned images, not text
- **Solution**: Use OCR tool (Tesseract) to convert to text first

### "Failed to parse" Error
- **Cause**: Corrupted or malformed file
- **Solution**: Re-save file or try different format

### Upload Hangs/Times Out
- **Cause**: Large file + slow network + many chunks
- **Solution**: Reduce file size or implement async processing

## Future Enhancements

- [ ] Add OCR support for scanned PDFs (Tesseract)
- [ ] Support more formats (RTF, Markdown, HTML)
- [ ] Implement async processing with job queue
- [ ] Add progress tracking for large uploads
- [ ] Support batch uploads (multiple files)
- [ ] Add file preview before processing
- [ ] Implement deduplication (skip if hash exists)
- [ ] Add file compression for storage
