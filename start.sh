#!/bin/bash

echo "🚀 Starting Magistra application..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Start the application
docker compose up -d

# Wait a moment for services to start
echo "⏳ Waiting for services to start..."
sleep 5

# Show status
docker compose ps

echo ""
echo "✅ Magistra is running!"
echo "📱 Application: http://localhost:5001"
echo "🗄️  Database: localhost:5432"
echo ""
echo "💡 Useful commands:"
echo "   ./stop.sh         - Stop the application"
echo "   ./logs.sh         - View logs"
echo "   docker compose ps - Check status"