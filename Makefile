.DEFAULT_GOAL := help

INPUT ?= data/knowledge/example.md
QUESTION ?= Was ist Dash-AI?
OLLAMA_PID_FILE := .ollama.pid
export INPUT QUESTION

.PHONY: help install install-dev start start-bg stop-bg pull ingest ask list test

help:
	@printf '%s\n' \
		'make install      Install Python application dependencies with uv' \
		'make install-dev  Install application and development dependencies' \
		'make start        Run Ollama in the foreground (Ctrl-C to stop)' \
		'make start-bg     Start Ollama in the background' \
		'make stop-bg      Stop the background Ollama process' \
		'make pull         Download the configured Ollama model' \
		'make ingest       Import the example (override with INPUT="path")' \
		'make ask          Ask the example question (override with QUESTION="...")' \
		'make list         List imported documents' \
		'make test         Run tests with development dependencies'

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
	uv run dash-ai ingest "$$INPUT"

ask:
	uv run dash-ai ask "$$QUESTION"

list:
	uv run dash-ai list

test:
	uv run --extra dev pytest
