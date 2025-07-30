#!/bin/bash

# RAGMilvusChatbot Docker Startup Script

echo "🚀 Starting RAGMilvusChatbot Docker deployment..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "📝 Please edit .env file with your configuration before continuing."
    echo "   You can set OPENAI_API_KEY and other required values."
    read -p "Press Enter to continue after editing .env file..."
fi

# Clean up any existing containers
echo "🧹 Cleaning up existing containers..."
docker compose down -v

# Remove old images to ensure fresh build
echo "🗑️  Removing old images..."
docker system prune -f

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p data/backend/vector_db
mkdir -p data/backend/etcd
mkdir -p data/backend/minio
mkdir -p data/raw_docs
mkdir -p data/store_docs

# Start services
echo "🔧 Starting services..."
docker compose up --build -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 30

# Check service status
echo "📊 Checking service status..."
docker compose ps

echo "✅ Deployment complete!"
echo ""
echo "🌐 Service URLs:"
echo "   Backend API: http://localhost:8001"
echo "   Milvus: http://localhost:19530"
echo "   Ollama: http://localhost:11434"
echo "   Web UI: http://localhost:3000"
echo ""
echo "📋 Useful commands:"
echo "   View logs: docker compose logs -f"
echo "   Stop services: docker compose down"
echo "   Restart: docker compose restart" 