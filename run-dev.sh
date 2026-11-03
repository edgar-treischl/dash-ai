#!/bin/bash
# Development server startup script
# Runs both the FastAPI backend and Vite frontend

set -e

echo "🚀 Starting Dash AI Development Environment"
echo ""

# Check if Ollama is running
echo "✓ Checking Ollama..."
if ! pgrep -f "ollama serve" > /dev/null; then
    echo "⚠️  Ollama is not running. Start it with: ollama serve"
    echo "   Then run this script again."
    exit 1
fi

# Start backend in background
echo "✓ Starting FastAPI backend on http://localhost:8000"
uv run uvicorn dash_ai.api.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Give backend time to start
sleep 2

# Start frontend in background
echo "✓ Starting Vite frontend on http://localhost:5173"
cd frontend
npm run dev &
FRONTEND_PID=$!

cd ..

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 Development environment is ready!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📱 Frontend:  http://localhost:5173"
echo "🔌 Backend:   http://localhost:8000"
echo "📚 API Docs:  http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Trap Ctrl+C to clean up both processes
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM

# Wait for both processes
wait
