#!/bin/bash

# Garmin Longevity Matrix MVP Startup Script
echo "🧬 Starting Garmin Longevity Matrix MVP..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Build and start all services
echo "🚀 Building and starting MVP services..."
docker-compose up --build -d

# Wait for services to be healthy
echo "⏳ Waiting for services to start..."
sleep 20

# Check service health
echo "🔍 Checking service health..."
docker-compose ps

# Test API connection
echo "🧪 Testing API connection..."
if curl -f http://localhost:8000/api/health/check > /dev/null 2>&1; then
    echo "✅ Backend API is running!"
else
    echo "❌ Backend API is not responding. Check logs with: docker-compose logs backend"
fi

# Test frontend connection
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is running!"
else
    echo "❌ Frontend is not responding. Check logs with: docker-compose logs frontend"
fi

echo ""
echo "🎉 Garmin Longevity Matrix MVP is starting up!"
echo "📊 Dashboard: http://localhost:3000"
echo "🔌 API: http://localhost:8000"
echo "📋 API Docs: http://localhost:8000/docs"
echo ""
echo "📝 To trigger data sync: curl -X POST http://localhost:8000/api/sync/trigger"
echo "📊 To check logs: docker-compose logs -f [service_name]"
echo "🛑 To stop: docker-compose down"