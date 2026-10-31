# 🚀 START HERE

This file is your quick reference to get started with Phase 1 implementation.

## What You Have

✅ **README.md** — Updated project vision with 4 key clarifications
✅ **PHASE_1_PLAN.md** — Detailed week-by-week implementation roadmap
✅ **.github/copilot-instructions.md** — Copilot context for future sessions

## The 4 Key Clarifications

Read sections 6.1–6.6 in README.md:

1. **Chunking** — Paragraph-based splitting, ~500 chars per chunk
2. **CLI** — 4 commands: `ingest`, `ask`, `list`, `delete`
3. **Retrieval** — SQLite FTS5, top-k=5, no filtering in Phase 1
4. **Context** — 4K tokens for mistral, truncate if needed

## Your Implementation Path

### Week 1 (Tasks 1.1–1.4)

1. **1.1 Project Setup** (5 hrs)
   - Create: `pyproject.toml`, `.gitignore`, directory structure
   - Dependencies: `pyyaml`, `requests`, `python-dotenv`, `pytest`

2. **1.2 Core Interfaces** (3 hrs)
   - File: `src/dash_ai/core/interfaces.py`
   - Define: `Document`, `ModelInterface`, `ReaderInterface`, `StorageInterface`

3. **1.3 Configuration** (2 hrs)
   - File: `src/dash_ai/core/config.py`
   - Template: `config/settings.yaml`
   - Support: YAML + environment override

4. **1.4 Markdown Ingestion** (4 hrs)
   - File: `src/dash_ai/ingestion/markdown.py`
   - Algorithm: Paragraph-based chunking (see PHASE_1_PLAN.md section 1.4)

### Week 2 (Tasks 1.5–1.11)

5. **1.5 SQLite Storage** (5 hrs)
   - File: `src/dash_ai/knowledge/storage.py`
   - Schema + CRUD + FTS5 search

6. **1.6 Ollama Integration** (3 hrs)
   - File: `src/dash_ai/models/ollama.py`
   - HTTP client + error handling + retries

7. **1.7 Retrieval Engine** (2 hrs)
   - File: `src/dash_ai/answering/retrieval.py`
   - Query storage, rank by relevance

8. **1.8 Answering Engine** (3 hrs)
   - File: `src/dash_ai/answering/engine.py`
   - RAG: retrieve → build prompt → model → format

9. **1.9 CLI Interface** (4 hrs)
   - File: `src/dash_ai/cli.py`
   - Commands: `ingest`, `ask`, `list`, `delete`

10. **1.10 Application Layer** (2 hrs)
    - File: `src/dash_ai/app.py`
    - Orchestrate components

11. **1.11 Entry Point** (1 hr)
    - File: `src/dash_ai/__main__.py`
    - Console script in `pyproject.toml`

## Success Criteria

By end of Week 2, you should be able to:

```bash
uv sync
ollama serve  # Terminal 2, with mistral loaded

dash-ai ingest data/knowledge/example.md
dash-ai ask "What is the topic?"
dash-ai list
pytest -v  # 70%+ coverage
```

## How to Use This Repo

1. **Start with README.md** — Understand sections 6.1–6.6 (clarifications)
2. **Open PHASE_1_PLAN.md** — Find your current task
3. **Follow the task** — Each has:
   - Specific files to create
   - Code sketches
   - Definition of Done
4. **Run tests** — `pytest tests/test_*.py`
5. **Check checklist** — Mark tasks done in PHASE_1_PLAN.md

## Questions?

- **Architecture unclear?** → Read README.md section 9 (architecture & modularity)
- **How to implement task X?** → See PHASE_1_PLAN.md section 1.X (code sketches)
- **What's the chunking algorithm?** → PHASE_1_PLAN.md section 1.4
- **What should tests look like?** → PHASE_1_PLAN.md testing strategy
- **How to run a single test?** → `pytest tests/test_config.py::test_loads_config`

## Next 30 Minutes

1. Read README.md sections 6.1–6.6 (5 mins)
2. Review PHASE_1_PLAN.md tasks 1.1–1.4 (10 mins)
3. Start task 1.1 — Create `pyproject.toml` (15 mins)
4. Commit: "Initial project setup"

Then continue task by task. Good luck! 🚀

---

**Estimated time:** ~39 hours for Phase 1 (just under 2 weeks full-time)  
**Test coverage target:** 70%+  
**Success metric:** End-to-end RAG working (ingest → ask → answer with sources)
