# API Testing Guide

**Academic Assignment Helper RAG - API Testing Documentation**

---

## Quick Start

### Prerequisites
- API running at `http://localhost:8000`
- curl or Postman installed
- Valid user account (create via registration)

### Base URL
```
http://localhost:8000
```

---

## Authentication Flow

### 1. Register New User
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "securepassword123"
  }'
```

**Expected Response:**
```json
{
  "id": 1,
  "email": "testuser@example.com",
  "is_active": true,
  "created_at": "2026-02-13T10:30:00"
}
```

### 2. Login to Get Token
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "securepassword123"
  }'
```

**Expected Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Save the token for subsequent requests:**
```bash
export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

## Assignment Management

### 3. Create Assignment
```bash
curl -X POST http://localhost:8000/assignments/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Data Structures Assignment",
    "description": "Implement binary search tree with insert, delete, and search operations",
    "due_date": "2026-03-15T23:59:59",
    "created_by": 1
  }'
```

**Expected Response:**
```json
{
  "id": 1,
  "title": "Data Structures Assignment",
  "description": "Implement binary search tree with insert, delete, and search operations",
  "due_date": "2026-03-15T23:59:59",
  "status": "draft",
  "created_by": 1,
  "created_at": "2026-02-13T10:35:00"
}
```

### 4. List All Assignments
```bash
curl -X GET http://localhost:8000/assignments/ \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response:**
```json
[
  {
    "id": 1,
    "title": "Data Structures Assignment",
    "description": "Implement binary search tree...",
    "due_date": "2026-03-15T23:59:59",
    "status": "draft",
    "created_by": 1,
    "created_at": "2026-02-13T10:35:00"
  }
]
```

### 5. Get Single Assignment
```bash
curl -X GET http://localhost:8000/assignments/1 \
  -H "Authorization: Bearer $TOKEN"
```

### 6. Update Assignment Status
```bash
curl -X PUT http://localhost:8000/assignments/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "published"
  }'
```

**Expected Response:**
```json
{
  "id": 1,
  "title": "Data Structures Assignment",
  "status": "published",
  "updated_at": "2026-02-13T10:40:00"
}
```

### 7. Filter Assignments
```bash
# Filter by status
curl -X GET "http://localhost:8000/assignments/?status=published" \
  -H "Authorization: Bearer $TOKEN"

# Filter by user
curl -X GET "http://localhost:8000/assignments/?user_id=1" \
  -H "Authorization: Bearer $TOKEN"

# Filter by due date
curl -X GET "http://localhost:8000/assignments/?due_before=2026-04-01T00:00:00" \
  -H "Authorization: Bearer $TOKEN"

# Combined filters
curl -X GET "http://localhost:8000/assignments/?status=published&user_id=1" \
  -H "Authorization: Bearer $TOKEN"
```

### 8. Delete Assignment
```bash
curl -X DELETE http://localhost:8000/assignments/1 \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response:**
```json
{
  "message": "Assignment deleted successfully"
}
```

---

## Health Checks

### 9. API Status
```bash
curl -X GET http://localhost:8000/
```

**Expected Response:**
```json
{
  "message": "Academic Assignment Helper RAG API",
  "status": "running",
  "version": "1.0.0"
}
```

### 10. Database Health
```bash
curl -X GET http://localhost:8000/health/db
```

**Expected Response:**
```json
{
  "status": "healthy",
  "database": "connected"
}
```

---

## Error Testing

### 11. Invalid Authentication
```bash
curl -X GET http://localhost:8000/assignments/ \
  -H "Authorization: Bearer invalid_token"
```

**Expected Response (401):**
```json
{
  "detail": "Could not validate credentials"
}
```

### 12. Missing Required Fields
```bash
curl -X POST http://localhost:8000/assignments/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Missing title field"
  }'
```

**Expected Response (422):**
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "title"],
      "msg": "Field required"
    }
  ]
}
```

### 13. Invalid Due Date
```bash
curl -X POST http://localhost:8000/assignments/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Past Due Assignment",
    "description": "This should fail",
    "due_date": "2020-01-01T00:00:00",
    "created_by": 1
  }'
```

**Expected Response (422):**
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "due_date"],
      "msg": "Due date must be in the future"
    }
  ]
}
```

### 14. Invalid Status
```bash
curl -X PUT http://localhost:8000/assignments/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "invalid_status"
  }'
```

**Expected Response (422):**
```json
{
  "detail": [
    {
      "type": "string_pattern_mismatch",
      "loc": ["body", "status"],
      "msg": "String should match pattern '^(draft|published|submitted|graded)$'"
    }
  ]
}
```

### 15. Assignment Not Found
```bash
curl -X GET http://localhost:8000/assignments/999 \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response (404):**
```json
{
  "detail": "Assignment not found"
}
```

---

## Postman Collection

### Import Collection
Create a new Postman collection with these requests:

1. **Environment Variables:**
   - `base_url`: `http://localhost:8000`
   - `token`: `{{access_token}}`

2. **Pre-request Script for Login:**
```javascript
pm.test("Login and set token", function () {
    pm.sendRequest({
        url: pm.environment.get("base_url") + "/auth/login",
        method: 'POST',
        header: {
            'Content-Type': 'application/json',
        },
        body: {
            mode: 'raw',
            raw: JSON.stringify({
                "email": "testuser@example.com",
                "password": "securepassword123"
            })
        }
    }, function (err, response) {
        if (response.json().access_token) {
            pm.environment.set("access_token", response.json().access_token);
        }
    });
});
```

---

## Test Scenarios

### Complete User Journey
```bash
#!/bin/bash
# Complete API test script

BASE_URL="http://localhost:8000"

echo "=== 1. Register User ==="
REGISTER_RESPONSE=$(curl -s -X POST $BASE_URL/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"journey@test.com","password":"testpass123"}')
echo $REGISTER_RESPONSE

echo -e "\n=== 2. Login ==="
LOGIN_RESPONSE=$(curl -s -X POST $BASE_URL/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"journey@test.com","password":"testpass123"}')
TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')
echo "Token: ${TOKEN:0:20}..."

echo -e "\n=== 3. Create Assignment ==="
CREATE_RESPONSE=$(curl -s -X POST $BASE_URL/assignments/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Assignment",
    "description": "Testing the complete flow",
    "due_date": "2026-12-31T23:59:59",
    "created_by": 1
  }')
ASSIGNMENT_ID=$(echo $CREATE_RESPONSE | jq -r '.id')
echo "Created Assignment ID: $ASSIGNMENT_ID"

echo -e "\n=== 4. List Assignments ==="
curl -s -X GET $BASE_URL/assignments/ \
  -H "Authorization: Bearer $TOKEN" | jq '.'

echo -e "\n=== 5. Update Assignment ==="
curl -s -X PUT $BASE_URL/assignments/$ASSIGNMENT_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "published"}' | jq '.'

echo -e "\n=== 6. Filter Published ==="
curl -s -X GET "$BASE_URL/assignments/?status=published" \
  -H "Authorization: Bearer $TOKEN" | jq '.'

echo -e "\n=== 7. Delete Assignment ==="
curl -s -X DELETE $BASE_URL/assignments/$ASSIGNMENT_ID \
  -H "Authorization: Bearer $TOKEN" | jq '.'

echo -e "\n=== Test Complete ==="
```

### Performance Testing
```bash
# Load test with multiple concurrent requests
for i in {1..10}; do
  curl -X GET http://localhost:8000/assignments/ \
    -H "Authorization: Bearer $TOKEN" &
done
wait
```

---

## Interactive API Documentation

### Swagger UI
Visit: `http://localhost:8000/docs`

Features:
- Interactive request forms
- Real-time response testing
- Schema validation
- Authentication testing
- Response examples

### ReDoc
Visit: `http://localhost:8000/redoc`

Features:
- Clean documentation layout
- Code examples in multiple languages
- Schema definitions
- Endpoint grouping

---

## Troubleshooting

### Common Issues

1. **401 Unauthorized**
   - Check token validity
   - Ensure Bearer prefix in Authorization header
   - Verify token hasn't expired

2. **422 Validation Error**
   - Check required fields
   - Validate data types
   - Ensure date formats are ISO 8601

3. **500 Internal Server Error**
   - Check database connection
   - Review server logs: `docker-compose logs backend`
   - Verify environment variables

4. **Connection Refused**
   - Ensure API is running: `docker-compose ps`
   - Check port 8000 is available
   - Verify Docker containers are healthy

### Debug Commands
```bash
# Check API status
curl -f http://localhost:8000/ || echo "API not responding"

# Check database health
curl -f http://localhost:8000/health/db || echo "Database issue"

# View logs
docker-compose logs -f backend

# Check container status
docker-compose ps
```

---

## Next Steps

After completing API testing:
1. Document any issues found
2. Test edge cases and error scenarios
3. Validate all response schemas
4. Perform load testing if needed
5. Update API documentation based on findings

For automated testing, consider implementing:
- Unit tests with pytest
- Integration tests with TestClient
- API contract testing
- Performance benchmarks