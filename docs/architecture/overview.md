# Architecture Overview

## System Design

dash-ai is a **local-first, modular RAG (Retrieval-Augmented Generation) system** that answers questions based on user-provided documents using local AI models.

```
┌─────────────┐
│   User CLI  │
└──────┬──────┘
       │
┌──────▼──────────────────┐
│   Application Layer     │ (orchestrates workflows)
└──────┬──────────────────┘
       │
   ┌───┴────────┬─────────────┬──────────────┐
   │            │             │              │
┌──▼──┐  ┌──────▼──┐  ┌──────▼──┐  ┌────────▼──┐
│ CLI │  │ Ingestion│  │ Storage │  │ Question  │
└─────┘  │(Markdown)│  │(SQLite) │  │ Answering │
         └──────────┘  └─────────┘  │  (RAG)    │
                                     └────┬──────┘
                                          │
                                    ┌─────▼──────┐
                                    │ Ollama LLM │
                                    │(local)     │
                                    └────────────┘
```

## Core Principle

**Do not tightly couple the application to any AI model, input format, or storage implementation.**

All pluggable components use abstract interfaces, enabling easy swaps:
- New storage backend? Implement `StorageInterface`
- Different input format? Implement `ReaderInterface`
- Different LLM? Implement `ModelInterface`

## Workflow

### Ingestion
1. User provides Markdown file(s)
2. `MarkdownReader` parses and chunks by paragraph (~500 chars)
3. Documents converted to common `Document` format
4. Stored in SQLite with FTS5 full-text search index

### Question-Answering
1. User asks a question via CLI
2. `Retriever` searches documents using full-text search
3. Top results combined into a prompt
4. Prompt sent to local Ollama model
5. AI-generated answer returned with source attribution

## Components

| Component | Purpose | Key File |
|-----------|---------|----------|
| **CLI** | User interface | `cli.py` |
| **App** | Orchestration layer | `app.py` |
| **Ingestion** | Parse & chunk documents | `ingestion/markdown.py` |
| **Storage** | Persist & search documents | `knowledge/storage.py` |
| **Model** | Local LLM interface | `models/ollama.py` |
| **Retrieval** | Full-text search | `answering/retrieval.py` |
| **Answering Engine** | RAG pipeline | `answering/engine.py` |
| **Interfaces** | Abstract contracts | `core/interfaces.py` |
| **Config** | Settings management | `core/config.py` |

## Data Flow Example

**User asks:** `"What is dash-ai?"`

1. `CLI.ask()` → `App.ask_question()`
2. `Retriever.retrieve()` → SQLite FTS5 search for "what", "is", "dash-ai"
3. Top 5 results scored and ranked
4. `AnsweringEngine.answer()` builds prompt:
   ```
   Context from documents:
   [retrieved chunks here]
   
   Question: What is dash-ai?
   Answer:
   ```
5. Prompt sent to Ollama via `OllamaModel.generate()`
6. Response returned with source attribution

## Storage Model

SQLite with FTS5 full-text search:
- One table: `documents` (id, title, content, source, metadata)
- One virtual table: `documents_fts` (full-text search index)
- Metadata stored as JSON for extensibility
- Auto-schema creation on first run

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Local-only** | Privacy-first; all data stays on user's machine |
| **SQLite** | No external dependencies; fast enough for phase 1 |
| **FTS5 search** | Good balance of speed and relevance; no ML needed |
| **Paragraph chunking** | Preserves document structure; simpler than semantic splitting |
| **Synchronous API** | Phase 1 simplicity; async can be added later |
| **Dependency injection** | Components stay loosely coupled and testable |

## Future Extensibility

The modular architecture supports:
- New input formats (PDF, CSV, JSON) → new `ReaderInterface` implementations
- Different storage backends (PostgreSQL, vector DB) → new `StorageInterface` implementations
- Alternative LLM runtimes (llama.cpp, MLX) → new `ModelInterface` implementations
- Vector search for semantic retrieval → new `RetrievalInterface` implementations
- Streaming responses → model interface enhancement
- Batch processing → new workflow layer

See [Roadmap](../guides/roadmap.md) for planned Phase 2 & 3 features.
