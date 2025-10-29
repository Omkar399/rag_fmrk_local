#!/bin/bash

# RAG Framework - Complete Stack Startup
# Starts FastAPI backend, Next.js frontend, and shows setup instructions

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo ""
echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║  🚀 RAG Framework - Complete Stack Startup                             ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if LM Studio is running
echo "🔍 Checking LM Studio status..."
if curl -s http://127.0.0.1:1234/v1/models > /dev/null 2>&1; then
    echo "✅ LM Studio is running"
else
    echo "⚠️  LM Studio is NOT running"
    echo "   Please start LM Studio with qwen2.5-7b-instruct-1m model"
    echo ""
fi

# Terminal setup function
setup_terminal() {
    local title=$1
    local cmd=$2
    local dir=$3
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📟 $title"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Command: $cmd"
    if [ -n "$dir" ]; then
        echo "Location: $dir"
    fi
    echo ""
}

# Show backend setup
setup_terminal "Terminal 1: FastAPI Backend" "uv run python backend/api.py" "$PROJECT_DIR"
echo "Starting backend on http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""

# Show frontend setup
setup_terminal "Terminal 2: Next.js Frontend" "npm run dev" "$PROJECT_DIR/frontend/nextjs"
echo "Starting frontend on http://localhost:3000"
echo ""

# Show requirements
echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║  📋 SETUP CHECKLIST                                                    ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Before running, ensure:"
echo ""
echo "✅ LM Studio"
echo "   - Application running"
echo "   - Model loaded: qwen2.5-7b-instruct-1m"
echo "   - Local Server started at http://127.0.0.1:1234"
echo ""
echo "✅ Backend Dependencies"
echo "   - Run: uv sync"
echo ""
echo "✅ Frontend Dependencies"
echo "   - Run: cd frontend/nextjs && npm install"
echo ""

# Ask if ready to start
read -p "Start services? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 1
fi

echo ""
echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║  🔧 STARTING SERVICES                                                  ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
echo ""

# Start backend in background
echo "Starting FastAPI backend..."
uv run python backend/api.py > /tmp/rag_backend.log 2>&1 &
BACKEND_PID=$!
echo "✅ Backend PID: $BACKEND_PID"

# Wait for backend to be ready
sleep 2

# Start frontend in background
echo "Starting Next.js frontend..."
cd "$PROJECT_DIR/frontend/nextjs"
npm run dev > /tmp/rag_frontend.log 2>&1 &
FRONTEND_PID=$!
echo "✅ Frontend PID: $FRONTEND_PID"

echo ""
echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║  ✨ SERVICES STARTED                                                   ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "🔌 Backend API: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"
echo "🤖 LM Studio: http://127.0.0.1:1234"
echo ""
echo "📝 Logs:"
echo "   Backend: tail -f /tmp/rag_backend.log"
echo "   Frontend: tail -f /tmp/rag_frontend.log"
echo ""
echo "🛑 To stop all services:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo ""

# Wait for user interrupt
wait
