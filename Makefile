.DEFAULT_GOAL := help

INPUT ?= data/knowledge/example.md
QUESTION ?= Wer ist Edgar Treischl?
OLLAMA_PID_FILE := .ollama.pid

.PHONY: help install install-dev start start-bg stop-bg pull ingest ask chat list test \
	api dev test-integration frontend build-frontend clean

help:
	@printf '%s\n' \
		'🚀 Installation & Setup' \
		'  make install      Install Python application dependencies with uv' \
		'  make install-dev  Install application and development dependencies' \
		'' \
		'⚙️  Ollama LLM Service' \
		'  make start        Run Ollama in the foreground (Ctrl-C to stop)' \
		'  make start-bg     Start Ollama in the background' \
		'  make stop-bg      Stop the background Ollama process' \
		'  make pull         Download the configured Ollama model' \
		'' \
		'📚 Knowledge Management' \
		'  make ingest       Import the example (override with INPUT="path")' \
		'  make list         List imported documents' \
		'' \
		'💬 Chat & Query' \
		'  make ask          Ask the example question (override with QUESTION="...")' \
		'  make chat         Start interactive chat session' \
		'' \
		'🌐 Frontend Integration' \
		'  make dev          Start both backend API and frontend together' \
		'  make api          Start only the FastAPI backend (port 8000)' \
		'  make frontend     Start only the Vite frontend (port 5173)' \
		'  make build-frontend Build frontend for production' \
		'  make test-integration Verify backend-frontend connection' \
		'' \
		'✅ Testing' \
		'  make test         Run tests with development dependencies'

install:
	uv sync

install-dev:
	uv sync --extra dev

start:
	ollama serve

start-bg:
	@if [ -f $(OLLAMA_PID_FILE) ]; then \
		echo "Ollama is already running (PID: $$(cat $(OLLAMA_PID_FILE)))"; \
		exit 1; \
	fi
	@echo "Starting Ollama in background..."
	@nohup ollama serve > /tmp/ollama.log 2>&1 & echo $$! > $(OLLAMA_PID_FILE)
	@echo "Ollama started with PID $$(cat $(OLLAMA_PID_FILE))"
	@sleep 2
	@echo "Check logs with: tail -f /tmp/ollama.log"

stop-bg:
	@if [ ! -f $(OLLAMA_PID_FILE) ]; then \
		echo "Ollama is not running"; \
		exit 1; \
	fi
	@pid=$$(cat $(OLLAMA_PID_FILE)); \
	echo "Stopping Ollama (PID: $$pid)..."; \
	kill $$pid || true; \
	rm -f $(OLLAMA_PID_FILE); \
	echo "Ollama stopped"

pull:
	@model=$$(uv run python -c 'from dash_ai.core.config import Config; print(Config().get("model", "name"))') && \
		ollama pull "$$model"

ingest:
	uv run dash-ai ingest "$(INPUT)"

ask:
	uv run dash-ai ask "$(QUESTION)"

chat:
	uv run dash-ai chat

list:
	uv run dash-ai list

test:
	uv run --extra dev pytest

# Frontend Integration Targets
api:
	@echo "🚀 Starting FastAPI backend (http://localhost:8000)"
	@echo "   API Documentation: http://localhost:8000/docs"
	@echo "   Press Ctrl+C to stop"
	uv run uvicorn dash_ai.api.main:app --reload --host 0.0.0.0 --port 8000

frontend:
	@echo "🚀 Starting Vite frontend (http://localhost:5173)"
	@echo "   Press Ctrl+C to stop"
	@cd frontend && npm run dev

dev:
	@echo "🎯 Starting Dash AI Development Environment"
	@echo ""
	@echo "✓ Frontend:  http://localhost:5173"
	@echo "✓ Backend:   http://localhost:8000"
	@echo "✓ API Docs:  http://localhost:8000/docs"
	@echo ""
	@echo "Press Ctrl+C to stop all services"
	@echo ""
	@./run-dev.sh

test-integration:
	@echo "🧪 Testing Frontend-Backend Integration"
	@./test-integration.sh

build-frontend:
	@echo "📦 Building frontend for production..."
	@cd frontend && npm run build
	@echo "✓ Built files available in frontend/dist/"

clean:
	@echo "🧹 Cleaning up..."
	@rm -rf frontend/dist
	@rm -rf frontend/node_modules/.vite
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@echo "✓ Cleaned"

