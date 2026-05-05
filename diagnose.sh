#!/bin/bash

echo "🔍 Academic Assignment Helper - System Diagnostics"
echo "=================================================="
echo ""

# Check Docker containers
echo "📦 Docker Containers:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep academic
echo ""

# Check backend health
echo "🏥 Backend Health:"
BACKEND_RESPONSE=$(curl -s http://localhost:8000/)
if echo "$BACKEND_RESPONSE" | grep -q "message"; then
    echo "✅ Backend is running"
    echo "$BACKEND_RESPONSE"
else
    echo "❌ Backend not responding"
fi
echo ""

# Test database connection
echo "💾 Database Connection:"
docker exec academic_db psql -U postgres -d academic_rag -c "SELECT COUNT(*) as user_count FROM users;" 2>/dev/null || echo "❌ Database connection failed"
echo ""

# Check if uploaded_by column exists
echo "🔧 Database Schema Check:"
COLUMN_CHECK=$(docker exec academic_db psql -U postgres -d academic_rag -t -c "SELECT column_name FROM information_schema.columns WHERE table_name='documents' AND column_name='uploaded_by';" 2>/dev/null)
if [ -n "$COLUMN_CHECK" ]; then
    echo "✅ uploaded_by column exists"
else
    echo "❌ uploaded_by column missing - run: docker exec academic_db psql -U postgres -d academic_rag -c 'ALTER TABLE documents ADD COLUMN uploaded_by INTEGER REFERENCES users(id);'"
fi
echo ""

# Check frontend
echo "🎨 Frontend:"
if [ -d "frontend/node_modules" ]; then
    echo "✅ Dependencies installed"
else
    echo "❌ Run: cd frontend && npm install"
fi
echo ""

# Test user creation and login
echo "🔐 Testing Auth Flow:"
TEST_EMAIL="diagnostic$(date +%s)@test.com"
echo "Creating user: $TEST_EMAIL"

REGISTER_RESPONSE=$(curl -s -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"test123\"}")

if echo "$REGISTER_RESPONSE" | grep -q "id"; then
    echo "✅ Registration successful"
    
    LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/auth/login \
      -H "Content-Type: application/json" \
      -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"test123\"}")
    
    if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
        echo "✅ Login successful"
        TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
        echo "Token: ${TOKEN:0:30}..."
        
        # Test upload
        echo ""
        echo "📤 Testing Upload:"
        echo "Test document" > /tmp/diag_test.txt
        UPLOAD_RESPONSE=$(curl -s -X POST http://localhost:8000/documents/upload \
          -H "Authorization: Bearer $TOKEN" \
          -F "file=@/tmp/diag_test.txt")
        
        if echo "$UPLOAD_RESPONSE" | grep -q '"id"'; then
            echo "✅ Upload successful"
            DOC_ID=$(echo "$UPLOAD_RESPONSE" | grep -o '"id":[0-9]*' | cut -d':' -f2)
            echo "Document ID: $DOC_ID"
            
            # Clean up test document
            curl -s -X DELETE "http://localhost:8000/documents/$DOC_ID" \
              -H "Authorization: Bearer $TOKEN" > /dev/null
            echo "✅ Cleanup successful"
        else
            echo "❌ Upload failed: $UPLOAD_RESPONSE"
        fi
    else
        echo "❌ Login failed: $LOGIN_RESPONSE"
    fi
else
    echo "❌ Registration failed: $REGISTER_RESPONSE"
fi

echo ""
echo "=================================================="
echo "✨ Diagnostic complete!"
echo ""
echo "Next steps:"
echo "1. Start frontend: cd frontend && npm run dev"
echo "2. Visit: http://localhost:5173/test"
echo "3. Run automated tests"
