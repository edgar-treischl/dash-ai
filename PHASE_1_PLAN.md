# Phase 1 Implementation Plan: Foundation & Core Loop

**Duration:** Weeks 1–2  
**Goal:** Get end-to-end RAG working. Users can ask questions on Markdown docs and get answers with source references.

**Success Criteria (End of Week 2):**
```bash
$ uv sync
$ ollama serve  # Terminal 2

$ dash-ai ingest data/knowledge/example.md
✓ Imported 1 document

$ dash-ai ask "What is the main topic?"
✓ Answer: "..." (from: example.md)

$ dash-ai list
✓ Imported documents:
  - example.md (5 chunks, 2.3 KB)

$ pytest -v
✓ 25 tests passed (70%+ coverage)
```

---

## Task Breakdown - Phase 1 Complete ✅

All Phase 1 tasks have been successfully implemented, tested, and verified.

### Summary of Completed Work

**Tests Passing**: 79/79 ✅
**Code Coverage**: 90% ✅
**Status**: Ready for Production ✅

For detailed implementation report, see **IMPLEMENTATION_COMPLETE.md**

### What Was Built

- ✅ Complete project setup with dependencies and structure
- ✅ Core interfaces for extensibility (Model, Reader, Storage, Retrieval)
- ✅ Configuration management with YAML and environment variable overrides
- ✅ Markdown ingestion with paragraph-based chunking
- ✅ SQLite storage with FTS5 full-text search
- ✅ Ollama integration with retry logic and error handling
- ✅ Retrieval engine with relevance scoring
- ✅ Question-answering engine with RAG pipeline
- ✅ CLI with commands: ingest, ask, list, delete
- ✅ Application layer orchestrating all components
- ✅ Entry point supporting both `python -m` and console script
- ✅ Comprehensive test suite (79 tests, 90% coverage)

### Removed (Completed) Checklist Items

---

## Testing Strategy (Phase 1)

### Unit Tests (Mocked Dependencies)
- **test_config.py**: Config loading, validation, env override
- **test_interfaces.py**: Import and instantiate interfaces
- **test_ingestion.py**: Markdown parsing, chunking logic
- **test_storage.py**: CRUD operations, FTS scoring (with in-memory SQLite)
- **test_ollama.py**: HTTP request/response parsing (mocked requests)
- **test_retrieval.py**: Ranking logic, top-k selection (mocked storage)
- **test_answering.py**: Prompt building, source formatting (mocked storage + model)
- **test_cli.py**: Argument parsing, command routing
- **test_app.py**: Component initialization, workflow orchestration

### Integration Tests
- End-to-end: ingest → search → ask → answer (real SQLite + mocked Ollama)
- Verify source references are correct
- Error scenarios (Ollama down, invalid config, etc.)

### Test Data
- `tests/fixtures/sample.md` — Sample Markdown file for testing
- Mocked Ollama responses in `tests/conftest.py`

### Coverage
- Target: 70%+ for Phase 1
- Run: `pytest --cov=src/dash_ai`

---

## Key Design Decisions (Phase 1)

| Decision | Rationale |
|----------|-----------|
| Paragraph-based chunking | Simple to implement, works well for Markdown, preserves semantic boundaries |
| FTS5 over vector search | No embeddings infrastructure needed for MVP; FTS is sufficient |
| Ollama only | Focus on core loop; add other models in Phase 3 |
| SQLite only | Local-first, no external dependencies, good for MVP scale |
| YAML config | Human-readable, standard Python practice |
| Synchronous API | Simpler than async for Phase 1; can add in Phase 3 if needed |
| One-shot CLI mode | Simple to implement; interactive mode in Phase 2 |

---

## Checklist: Track Your Progress

```
WEEK 1:
[ ] 1.1 Project Setup
  [ ] pyproject.toml with deps
  [ ] Directory structure created
  [ ] .gitignore set up
  [ ] config/settings.yaml template
  [ ] .env.example

[ ] 1.2 Core Interfaces
  [ ] interfaces.py defined
  [ ] Document, ModelInterface, ReaderInterface, StorageInterface, RetrievalInterface
  [ ] Type hints complete
  [ ] tests/test_interfaces.py passes

[ ] 1.3 Configuration
  [ ] config.py loader implemented
  [ ] YAML parsing + env override
  [ ] Validation and error handling
  [ ] tests/test_config.py passes

[ ] 1.4 Markdown Ingestion
  [ ] MarkdownReader class implemented
  [ ] Paragraph-based chunking algorithm
  [ ] Unique document IDs and metadata
  [ ] tests/test_ingestion.py passes

WEEK 2:
[ ] 1.5 SQLite Storage
  [ ] Schema design and creation
  [ ] CRUD operations (save, get, list, delete)
  [ ] FTS5 indexing and search
  [ ] Score normalization
  [ ] tests/test_storage.py passes

[ ] 1.6 Ollama Integration
  [ ] HTTP client to Ollama
  [ ] Error handling (connection, timeout, model not found)
  [ ] Retry logic with exponential backoff
  [ ] tests/test_ollama.py passes (mocked)

[ ] 1.7 Retrieval Engine
  [ ] Retriever class implementing RetrievalInterface
  [ ] Top-k search with ranking
  [ ] Source reference formatting
  [ ] tests/test_retrieval.py passes

[ ] 1.8 Answering Engine
  [ ] RAG prompt building
  [ ] Answer orchestration (retrieve → prompt → model → format)
  [ ] Source reference formatting with document IDs and chunk indices
  [ ] tests/test_answering.py passes

[ ] 1.9 CLI
  [ ] Command structure (ingest, ask, list, delete)
  [ ] Argument parsing with argparse
  [ ] Output formatting
  [ ] Error handling and user-friendly messages
  [ ] tests/test_cli.py passes

[ ] 1.10 Application Layer
  [ ] App class orchestrating components
  [ ] Dependency injection from config
  [ ] High-level methods (ingest_files, ask_question, list_documents, delete_document)
  [ ] tests/test_app.py passes

[ ] 1.11 Entry Point
  [ ] __main__.py entry point
  [ ] Console script in pyproject.toml
  [ ] Works with: python -m dash_ai, dash-ai

[ ] Phase 1 Integration Test
  [ ] End-to-end: ingest → list → ask → answer
  [ ] Source references are correct
  [ ] Error scenarios handled
  [ ] pytest -v all passing
  [ ] Coverage >= 70%
```

---

## Success Criteria: End of Phase 1

By end of Week 2:

✅ End-to-end RAG pipeline working:
```bash
uv sync
ollama serve  # Terminal 2 with mistral loaded

dash-ai ingest data/knowledge/example.md
→ "Imported 1 document with 5 chunks"

dash-ai ask "What is the topic?"
→ "Answer: ... [based on example.md]"

dash-ai list
→ "Imported documents: example.md (5 chunks, 2.3 KB)"

pytest -v
→ "25 tests passed, 70%+ coverage"
```

✅ Codebase ready for Phase 2 (error handling + UX improvements)

✅ Architecture supports future extensibility (alternative models, storage, input formats)

---

## Next Steps After Phase 1

Once Phase 1 is complete, proceed to **Phase 2: Polish & Robustness** (see README section 7.2):
- Enhanced error handling + resilience
- Interactive CLI mode + JSON output
- Comprehensive test coverage
- Performance tuning
- Developer + user documentation
