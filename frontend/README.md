# Academic Assignment Helper - Frontend

## Quick Start

```bash
npm install
npm run dev
```

Access at: http://localhost:5173

## Test Credentials

Create a new account or use:
- Email: `newuser@test.com`
- Password: `password123`

## Testing the App

1. **Visit Test Page**: http://localhost:5173/test
   - Click "Run All Tests" to verify backend connectivity
   - All tests should pass (green)

2. **Register**: Create a new account
3. **Login**: Use your credentials
4. **Dashboard**: Upload documents and ask questions

## Troubleshooting

### Login Returns 401 Error

**Cause**: Rate limiting (5 attempts per 15 minutes) or wrong password

**Solutions**:
1. Wait 15 minutes if rate limited
2. Create a new account with different email
3. Check backend logs: `docker logs academic_api`

### Backend Connection Failed

**Check**:
```bash
# Verify backend is running
curl http://localhost:8000/

# Check .env file
cat .env
# Should have: VITE_API_URL=http://localhost:8000
```

### CORS Errors

Backend CORS is configured for all origins. If you see CORS errors:
1. Restart backend: `docker-compose restart backend`
2. Check browser console for actual error

## API Endpoints

- `POST /auth/register` - Create account
- `POST /auth/login` - Get JWT token
- `GET /documents/` - List documents
- `POST /documents/upload` - Upload file
- `DELETE /documents/{id}` - Delete document
- `POST /query/ask` - Ask question about document

## Features

✅ JWT Authentication with localStorage
✅ Protected routes
✅ File upload (PDF, DOCX, TXT)
✅ Document management (list, delete)
✅ RAG-powered Q&A with source citations
✅ **Plagiarism Detection** (hash + semantic similarity)
✅ Chat history persistence
✅ Error handling and loading states
✅ Responsive design with dark mode
