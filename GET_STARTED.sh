#!/bin/bash

echo "🚀 RAG Pipeline Setup Script"
echo "=============================="
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed"
    echo "Install it from: https://github.com/astral-sh/uv"
    exit 1
fi

echo "✓ uv found: $(uv --version)"
echo ""

# Install dependencies
echo "📦 Installing dependencies with uv..."
uv sync

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✓ Dependencies installed"
echo ""

# Create data directory
if [ ! -d "data" ]; then
    echo "📂 Creating data/ directory..."
    mkdir -p data
fi

echo "✓ Data directory ready"
echo ""

# Run example
echo "🧪 Running example script..."
echo ""
uv run python3 example_usage.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Add your documents to data/"
echo "  2. Run: uv run python3 -m app.pipeline --index"
echo "  3. Query: uv run python3 -m app.pipeline"
echo ""
echo "For more info, see:"
echo "  - QUICKSTART.md"
echo "  - README.md"
echo "  - IMPLEMENTATION_SUMMARY.md"
