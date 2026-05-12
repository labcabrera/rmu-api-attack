#!/bin/bash

# Startup script for RMU Attack API development

set -euo pipefail

export UV_CACHE_DIR="${UV_CACHE_DIR:-/tmp/uv-cache}"
export UV_LINK_MODE="${UV_LINK_MODE:-copy}"

echo "🚀 Starting RMU API Attack..."
echo "==============================================="

echo "📦 Synchronizing dependencies with uv..."
uv sync --all-groups

echo "✅ Dependencies verified"
echo ""
echo "🌐 Starting FastAPI server..."
echo "📚 Documentation available at: http://localhost:8000/docs"
echo "🔄 Swagger UI at: http://localhost:8000/docs"
echo "📖 ReDoc at: http://localhost:8000/redoc"
echo ""
echo "To stop the server press Ctrl+C"
echo "==============================================="

# Start the server
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
