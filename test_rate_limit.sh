#!/bin/bash

echo "🧪 Testing Rate Limiting"
echo "========================"
echo ""

echo "Test 1: Health endpoint (no rate limit)"
echo "----------------------------------------"
for i in {1..3}; do
  echo "Request $i:"
  curl -s http://localhost:8000/health | jq -r '.status'
done

echo ""
echo "Test 2: Login endpoint (5 per 15 minutes)"
echo "-------------------------------------------"
echo "Sending 6 login requests rapidly..."
echo ""

for i in {1..6}; do
  echo "Request $i:"
  response=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST http://localhost:8000/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"wrong"}')
  
  http_code=$(echo "$response" | grep "HTTP_CODE" | cut -d: -f2)
  body=$(echo "$response" | sed '/HTTP_CODE/d')
  
  if [ "$http_code" == "429" ]; then
    echo "  ❌ RATE LIMITED! (HTTP 429)"
    echo "  Response: $body" | jq -r '.detail.error' 2>/dev/null || echo "$body"
  elif [ "$http_code" == "401" ]; then
    echo "  ✅ Request allowed (HTTP 401 - wrong password, but not rate limited)"
  else
    echo "  Status: HTTP $http_code"
    echo "  Body: $body"
  fi
  echo ""
done

echo "✅ Rate limiting test complete!"
