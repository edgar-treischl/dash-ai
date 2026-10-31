# Sample Knowledge Base Document

## What is Dash-AI?

Dash-AI is a local-first artificial intelligence knowledge assistant designed to help users answer questions based on their own documents. Built with Python and powered by Ollama, it keeps all data locally on your machine without requiring cloud services.

## Key Features

The system provides several important capabilities:

- **Local Processing**: All data remains on your computer. No uploads to external services.
- **Full-Text Search**: Indexes documents using SQLite full-text search for fast retrieval.
- **Source References**: Every answer includes citations showing which documents were used.
- **Modular Design**: Components are independent and can be swapped out easily.

## Technology Stack

Dash-AI uses modern, lightweight technologies:

- Python 3.10+ for the core application
- SQLite for local data storage with FTS5 indexing
- Ollama for running language models locally
- YAML for configuration management
- Pytest for comprehensive testing

## Getting Started

To use Dash-AI, follow these simple steps:

1. Ensure Ollama is running on your system
2. Install dash-ai using uv sync
3. Ingest your Markdown documents
4. Ask questions and receive answers with sources

The system is designed to be easy to extend with new features over time.

## Use Cases

Dash-AI is perfect for:

- Personal knowledge management systems
- Team documentation Q&A
- Research assistant workflows
- Local AI experimentation without cloud dependencies
