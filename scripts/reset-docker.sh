#!/bin/bash

# RAGMilvusChatbot Docker Reset Script for Linux/Mac

echo "🚀 Starting RAGMilvusChatbot Docker reset and deployment..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "📝 Please edit .env file with your configuration before continuing."
    echo "   You can set OPENAI_API_KEY and other required values."
    read -p "Press Enter to continue after editing .env file..."
fi

# Stop and remove all containers and volumes
echo "🧹 Stopping and removing all containers and volumes..."
docker compose down -v

# Remove all Docker images to ensure fresh build
echo "🗑️  Removing all Docker images..."
docker system prune -af

# Clear data directories to fix Milvus node ID issues
echo "🗂️  Clearing data directories..."
rm -rf data/backend/vector_db/*
rm -rf data/backend/etcd/*
rm -rf data/backend/minio/*

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
sleep 60

# Check service status
echo "📊 Checking service status..."
docker compose ps

echo "✅ Reset and deployment complete!"
echo ""
echo "🌐 Service URLs:"
echo "   Backend API: http://localhost:8001"
echo "   Milvus: http://localhost:19530"
echo "   Ollama: http://localhost:11434"
echo "   Web UI: http://localhost:3000"
echo "   MinIO Console: http://localhost:9001"
echo ""
echo "📋 Useful commands:"
echo "   View logs: docker compose logs -f"
echo "   Stop services: docker compose down"
echo "   Restart: docker compose restart"
echo ""
echo "🔍 To monitor deployment progress:"
echo "   docker compose logs -f" 