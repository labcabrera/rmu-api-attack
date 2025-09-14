# Activate virtual environment
if [ -d ".venv" ]; then
    echo "📦 Activating virtual environment..."
    source .venv/bin/activate
else
    echo "❌ Virtual environment not found. Run 'python -m venv .venv' first."
    exit 1
fi

pytest tests/ -v