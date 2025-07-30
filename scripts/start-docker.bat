@echo off
REM RAGMilvusChatbot Docker Startup Script for Windows

echo 🚀 Starting RAGMilvusChatbot Docker deployment...

REM Check if .env file exists
if not exist .env (
    echo ⚠️  .env file not found. Creating from template...
    copy .env.example .env
    echo 📝 Please edit .env file with your configuration before continuing.
    echo    You can set OPENAI_API_KEY and other required values.
    pause
)

REM Clean up any existing containers
echo 🧹 Cleaning up existing containers...
docker compose down -v

REM Remove old images to ensure fresh build
echo 🗑️  Removing old images...
docker system prune -f

REM Create necessary directories
echo 📁 Creating necessary directories...
if not exist data\backend\vector_db mkdir data\backend\vector_db
if not exist data\backend\etcd mkdir data\backend\etcd
if not exist data\backend\minio mkdir data\backend\minio
if not exist data\raw_docs mkdir data\raw_docs
if not exist data\store_docs mkdir data\store_docs

REM Start services
echo 🔧 Starting services...
docker compose up --build -d

REM Wait for services to be healthy
echo ⏳ Waiting for services to be healthy...
timeout /t 30 /nobreak > nul

REM Check service status
echo 📊 Checking service status...
docker compose ps

echo ✅ Deployment complete!
echo.
echo 🌐 Service URLs:
echo    Backend API: http://localhost:8001
echo    Milvus: http://localhost:19530
echo    Ollama: http://localhost:11434
echo    Web UI: http://localhost:3000
echo.
echo 📋 Useful commands:
echo    View logs: docker compose logs -f
echo    Stop services: docker compose down
echo    Restart: docker compose restart

pause 