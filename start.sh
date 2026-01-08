#!/bin/bash

echo "🚀 Starting Academic Assignment Helper API..."

# Start the services
docker-compose up -d

echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
echo "📊 Service Status:"
docker-compose ps

echo "🔍 Testing API endpoints..."

# Test health endpoint
echo "Testing health endpoint:"
curl -X GET "http://localhost:8000/health/db" -H "accept: application/json"

echo -e "\n\n📚 API Documentation available at:"
echo "http://localhost:8000/docs"

echo -e "\n🔧 n8n Automation available at:"
echo "http://localhost:5678 (admin/admin)"

echo -e "\n✅ Setup complete! Your API is ready for development."