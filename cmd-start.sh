#!/bin/bash

# Startup script for RMU Attack API development

echo "🚀 Starting RMU API Attack..."
echo "==============================================="

# Activate virtual environment
if [ -d ".venv" ]; then
    echo "📦 Activating virtual environment..."
    source .venv/bin/activate
else
    echo "❌ Virtual environment not found. Run 'python -m venv .venv' first."
    exit 1
fi

# Verify dependencies installation
echo "🔍 Verifying dependencies..."
pip list | grep fastapi > /dev/null
if [ $? -ne 0 ]; then
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
fi

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
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
