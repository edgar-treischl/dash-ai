.DEFAULT_GOAL := help

INPUT ?= data/knowledge/example.md
QUESTION ?= What is this project about?
export INPUT QUESTION

.PHONY: help install install-dev start pull ingest ask list test

help:
	@printf '%s\n' \
		'make install      Install Python application dependencies with uv' \
		'make install-dev  Install application and development dependencies' \
		'make start        Run Ollama in the foreground (Ctrl-C to stop)' \
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
