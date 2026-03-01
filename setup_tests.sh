#!/bin/bash

echo "🚀 Academic Assignment Helper - Test Setup"
echo "=========================================="

# Check if docker-compose is running
if ! docker-compose ps | grep -q "Up"; then
    echo "📦 Starting Docker containers..."
    docker-compose up -d
    echo "⏳ Waiting for services to be ready..."
    sleep 10
else
    echo "✅ Docker containers already running"
fi

# Show container status
echo ""
echo "📊 Container Status:"
docker-compose ps

# Run Python setup script
echo ""
echo "🔧 Running database setup..."
cd backend && python3 tests/test_setup.py

echo ""
echo "✅ Setup complete! Ready for testing."
