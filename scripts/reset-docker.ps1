# RAGMilvusChatbot Docker Reset Script for Windows

Write-Host "🚀 Starting RAGMilvusChatbot Docker reset and deployment..." -ForegroundColor Green

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  .env file not found. Creating from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "📝 Please edit .env file with your configuration before continuing." -ForegroundColor Yellow
    Write-Host "   You can set OPENAI_API_KEY and other required values." -ForegroundColor Yellow
    Read-Host "Press Enter to continue after editing .env file..."
}

# Stop and remove all containers and volumes
Write-Host "🧹 Stopping and removing all containers and volumes..." -ForegroundColor Yellow
docker compose down -v

# Remove all Docker images to ensure fresh build
Write-Host "🗑️  Removing all Docker images..." -ForegroundColor Yellow
docker system prune -af

# Clear data directories to fix Milvus node ID issues
Write-Host "🗂️  Clearing data directories..." -ForegroundColor Yellow
if (Test-Path "data\backend\vector_db") {
    Remove-Item -Recurse -Force "data\backend\vector_db\*" -ErrorAction SilentlyContinue
}
if (Test-Path "data\backend\etcd") {
    Remove-Item -Recurse -Force "data\backend\etcd\*" -ErrorAction SilentlyContinue
}
if (Test-Path "data\backend\minio") {
    Remove-Item -Recurse -Force "data\backend\minio\*" -ErrorAction SilentlyContinue
}

# Create necessary directories
Write-Host "📁 Creating necessary directories..." -ForegroundColor Yellow
if (-not (Test-Path "data\backend\vector_db")) { New-Item -ItemType Directory -Path "data\backend\vector_db" -Force }
if (-not (Test-Path "data\backend\etcd")) { New-Item -ItemType Directory -Path "data\backend\etcd" -Force }
if (-not (Test-Path "data\backend\minio")) { New-Item -ItemType Directory -Path "data\backend\minio" -Force }
if (-not (Test-Path "data\raw_docs")) { New-Item -ItemType Directory -Path "data\raw_docs" -Force }
if (-not (Test-Path "data\store_docs")) { New-Item -ItemType Directory -Path "data\store_docs" -Force }

# Start services
Write-Host "🔧 Starting services..." -ForegroundColor Green
docker compose up --build -d

# Wait for services to be healthy
Write-Host "⏳ Waiting for services to be healthy..." -ForegroundColor Yellow
Start-Sleep -Seconds 60

# Check service status
Write-Host "📊 Checking service status..." -ForegroundColor Green
docker compose ps

Write-Host "✅ Reset and deployment complete!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Service URLs:" -ForegroundColor Cyan
Write-Host "   Backend API: http://localhost:8001" -ForegroundColor White
Write-Host "   Milvus: http://localhost:19530" -ForegroundColor White
Write-Host "   Ollama: http://localhost:11434" -ForegroundColor White
Write-Host "   Web UI: http://localhost:3000" -ForegroundColor White
Write-Host "   MinIO Console: http://localhost:9001" -ForegroundColor White
Write-Host ""
Write-Host "📋 Useful commands:" -ForegroundColor Cyan
Write-Host "   View logs: docker compose logs -f" -ForegroundColor White
Write-Host "   Stop services: docker compose down" -ForegroundColor White
Write-Host "   Restart: docker compose restart" -ForegroundColor White
Write-Host ""
Write-Host "🔍 To monitor deployment progress:" -ForegroundColor Yellow
Write-Host "   docker compose logs -f" -ForegroundColor White

Read-Host "Press Enter to continue..." 