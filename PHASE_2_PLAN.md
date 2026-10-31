# Phase 2: Polish & Robustness Implementation Plan

**Duration:** Weeks 3–4 (estimated 30–40 hours)
**Objective:** Transform Phase 1's working RAG system into a production-ready tool with enhanced error handling, improved UX, comprehensive testing, and documentation.

⏳ Task 2.5: Test Suite Extensions (PENDING)
• ✅ Task 2.6: Performance Profiling (COMPLETE)
• ⏳ Task 2.7: User Documentation (PENDING)
• ⏳ Task 2.8: Developer Documentation (PENDING)

---

## Overview

Phase 2 focuses on **robustness, usability, and documentation**. The core RAG pipeline from Phase 1 already works; now we add:

1. **Enhanced error handling** — Graceful degradation, helpful error messages, recovery strategies
2. **Interactive CLI mode** — Multi-turn conversations, command history, interactive prompts
3. **Advanced CLI features** — JSON output format, progress indicators, better formatting
4. **Comprehensive test coverage** — Edge cases, integration tests, performance benchmarks
5. **Performance tuning** — Profiling, caching, optimization opportunities
6. **Expanded documentation** — User guide, troubleshooting, developer guide, examples

---

## Success Criteria

- ✅ All Phase 1 tests still pass
- ✅ 90%+ test coverage maintained
- ✅ Interactive mode works (multi-turn conversations)
- ✅ JSON output format supported
- ✅ Progress indicators shown during long operations
- ✅ All error cases handled gracefully with helpful messages
- ✅ User guide and troubleshooting docs complete
- ✅ Performance profiling completed
- ✅ Edge cases covered (empty results, large files, malformed input)
- ✅ System works offline after initial model download

---

## Task Breakdown

### Week 3: Enhanced Error Handling & Interactive CLI

#### 2.1 Advanced Error Handling (4 hrs)

**Objective:** Implement comprehensive error handling across all components.

**Files to Modify:**
- `src/dash_ai/core/errors.py` (new)
- `src/dash_ai/cli.py` (update)
- `src/dash_ai/app.py` (update)
- `src/dash_ai/models/ollama.py` (update)
- `src/dash_ai/knowledge/storage.py` (update)

**What to implement:**

1. **Create error hierarchy** (`core/errors.py`):
   ```python
   class DashAIError(Exception):
       """Base exception for all Dash-AI errors."""
       pass

   class ConfigurationError(DashAIError):
       """Configuration is invalid or missing."""
       pass

   class StorageError(DashAIError):
       """Database/storage operation failed."""
       pass

   class ModelError(DashAIError):
       """LLM or model operation failed."""
       pass

   class RetrievalError(DashAIError):
       """Document retrieval failed."""
       pass

   class IngestionError(DashAIError):
       """Document ingestion failed."""
       pass
   ```

2. **Update components to raise custom exceptions:**
   - `OllamaModel`: Catch HTTP errors, model errors, timeout → raise `ModelError`
   - `SQLiteStorage`: Database errors → raise `StorageError`
   - `MarkdownReader`: File errors, parsing errors → raise `IngestionError`
   - `Config`: Missing/invalid config → raise `ConfigurationError`

3. **Update CLI to handle exceptions:**
   - Catch `DashAIError` and subclasses
   - Display helpful error messages with context
   - Suggest recovery steps (e.g., "Is Ollama running?")
   - Exit with appropriate error codes
   - Log full traceback in verbose mode (optional)

4. **Add error recovery:**
   - Retry logic for transient failures (network, timeouts)
   - Graceful degradation (e.g., partial results)
   - Clear recovery instructions in error messages

**Definition of Done:**
- Custom exception hierarchy created
- All components raise appropriate exceptions
- CLI catches and formats exceptions nicely
- Error messages include recovery suggestions
- Tests verify error handling paths
- No unhandled exceptions reach user

---

#### 2.2 Interactive CLI Mode (5 hrs)

**Objective:** Implement multi-turn interactive conversation mode.

**Files to Modify:**
- `src/dash_ai/cli.py` (major update)
- `src/dash_ai/app.py` (add interactive method)

**What to implement:**

1. **Interactive REPL:**
   - New command: `dash-ai chat` or `dash-ai interactive`
   - Multi-turn conversation in a session
   - Persistent chat context (optional: save to file)
   - Graceful exit with `exit`, `quit`, or Ctrl+D

2. **Command history:**
   - Track questions asked in session
   - Display command count
   - Optional: save history to `.dash_ai_history` file

3. **Improved prompting:**
   - Clear input prompt: `> Ask a question: `
   - Visual feedback while generating answers (spinner or dots)
   - Numbered questions in session

4. **Session metadata:**
   - Start time
   - Number of questions asked
   - Total generation time
   - Tokens used (if available from Ollama)

**Interactive mode flow:**
```
$ dash-ai chat
Starting interactive session...
Type 'exit' to quit. Type 'help' for commands.

> Ask a question: What is Dash-AI?
Thinking... [spinner animation]

Answer: Dash-AI is a local-first AI knowledge assistant...
Sources: data/knowledge/example.md

> Ask a question: Tell me more about the features
Thinking...

Answer: The core features include...

> Ask a question: exit
Session complete. Asked 2 questions in 5.2s.
```

**Definition of Done:**
- `dash-ai chat` command works
- Multi-turn conversation maintained
- Graceful exit with summary
- Command history tracked
- Tests verify interactive flow (mock input/output)
- Performance acceptable (< 1s response time)

---

#### 2.3 JSON Output Format (3 hrs)

**Objective:** Support structured output for programmatic use.

**Files to Modify:**
- `src/dash_ai/cli.py` (add `--json` flag)
- `src/dash_ai/app.py` (add JSON formatting method)

**What to implement:**

1. **Global `--json` flag:**
   - Available on all commands: `ingest`, `ask`, `list`, `delete`
   - Outputs structured JSON instead of human text

2. **JSON output schemas:**

   **For `ingest --json`:**
   ```json
   {
     "status": "success",
     "files_imported": 1,
     "chunks_created": 42,
     "documents": [
       {"id": "doc1-0", "chunks": 2, "source": "file.md"}
     ]
   }
   ```

   **For `ask --json`:**
   ```json
   {
     "status": "success",
     "question": "What is Dash-AI?",
     "answer": "Dash-AI is...",
     "sources": [
       {
         "document_id": "doc1-5",
         "source_file": "data/knowledge/example.md",
         "relevance_score": 0.95,
         "excerpt": "Dash-AI is a local-first..."
       }
     ],
     "generation_time_ms": 1234
   }
   ```

   **For `list --json`:**
   ```json
   {
     "status": "success",
     "documents": [
       {
         "id": "doc1-0",
         "source": "data/knowledge/example.md",
         "chunks": 42,
         "imported_at": "2026-10-31T14:45:00"
       }
     ],
     "total_documents": 1,
     "total_chunks": 42
   }
   ```

   **Error response (all commands):**
   ```json
   {
     "status": "error",
     "error_type": "ModelError",
     "error_message": "Ollama connection failed",
     "suggestion": "Is Ollama running?"
   }
   ```

3. **Validation:**
   - JSON is valid and parseable
   - Schema is consistent
   - Timestamps in ISO 8601 format

**Definition of Done:**
- `--json` flag works on all commands
- JSON output is valid and structured
- Tests verify JSON output format
- Documentation shows example JSON responses
- Error responses include JSON

---

#### 2.4 Progress Indicators (2 hrs)

**Objective:** Add visual feedback during long operations.

**Files to Modify:**
- `src/dash_ai/cli.py` (add spinner/progress)
- `src/dash_ai/app.py` (add timing info)

**What to implement:**

1. **Spinner during model generation:**
   - Show spinner while Ollama is generating answer
   - Replace with answer when done
   - Use simple ASCII spinner: `|`, `/`, `-`, `\`

2. **Progress bar for batch ingestion:**
   - For `ingest <directory>`, show progress: `[████░░░░░░] 4/10 files`
   - Update as files are processed

3. **Timing information:**
   - Display generation time: "Generated in 1.23s"
   - Display search time: "Retrieved documents in 0.05s"
   - Display total time: "Total time: 1.28s"

4. **No progress for `--json` output:**
   - Suppress spinner/progress when `--json` is used
   - Spinners only go to stderr, JSON to stdout

**Definition of Done:**
- Spinner visible during generation
- Progress bar shown for batch operations
- Timing displayed in output
- Works with `--json` flag (no spurious output)
- Tests verify timing calculations

---

### Week 4: Testing, Performance & Documentation

#### 2.5 Comprehensive Test Suite Extensions (6 hrs)

**Objective:** Extend test coverage to 95%+ and cover edge cases.

**Files to Create/Modify:**
- `tests/test_errors.py` (new)
- `tests/test_cli.py` (expand for interactive mode)
- `tests/test_edge_cases.py` (new)
- `tests/test_performance.py` (new)

**What to test:**

1. **Error handling tests** (`test_errors.py`):
   - Custom exception hierarchy
   - Error message formatting
   - Recovery suggestions
   - Error code precedence
   - All components raise appropriate errors

2. **Interactive mode tests** (`test_cli.py` expansion):
   - Multi-turn conversation mock
   - Exit handling
   - Session metadata
   - Command history
   - Invalid input handling

3. **Edge cases** (`test_edge_cases.py`):
   - Empty database (ask with no documents)
   - Very large files (> 1MB Markdown)
   - Malformed input (invalid UTF-8, corrupt chunks)
   - Network errors (Ollama unavailable)
   - Disk full (storage error)
   - Very long questions (> 10K chars)
   - Special characters in queries
   - Unicode handling
   - Database corruption recovery

4. **Performance tests** (`test_performance.py`):
   - Ingestion speed: 1MB file < 1s
   - Search speed: retrieve 5 docs < 50ms
   - Generation speed: model.generate < 30s
   - Memory usage: baseline < 100MB

**Definition of Done:**
- Test coverage ≥ 95%
- All edge cases covered
- Performance benchmarks recorded
- Tests pass consistently
- No flaky tests

---

#### 2.6 Performance Profiling & Optimization (4 hrs) — ✅ COMPLETE

**Objective:** Profile the system and identify/implement optimizations.

**Files to Modify:**
- `src/dash_ai/app.py` (optimize if needed)
- `src/dash_ai/knowledge/storage.py` (optimize if needed)
- `src/dash_ai/answering/retrieval.py` (optimize if needed)

**What to do:**

1. **Profiling:**
   - Use `cProfile` to identify bottlenecks
   - Profile `ingest`, `ask`, and `list` operations
   - Measure CPU time, wall-clock time, and memory
   - Create `docs/profiling_results.md` with findings

2. **Optimization opportunities to investigate:**
   - Database query optimization (indexes, batch inserts)
   - FTS5 search optimization (query parsing)
   - Document chunking efficiency
   - Memory usage during large ingestion
   - Caching repeated searches

3. **Implement quick wins:**
   - Add database indexes if missing
   - Batch insert for multiple documents
   - Limit result set in search queries
   - Cache frequently accessed data

4. **Document findings:**
   - Create `docs/performance.md`
   - Include profiling results
   - Suggest future optimizations
   - Include memory/CPU baseline

**Definition of Done:**
- Profiling completed and documented
- Bottlenecks identified
- Quick wins implemented
- Performance remains consistent (< 2s for typical ask)
- Benchmarks recorded in documentation

---

#### 2.7 User Documentation (5 hrs)

**Objective:** Create comprehensive user-facing documentation.

**Files to Create:**
- `docs/user_guide.md` (new)
- `docs/troubleshooting.md` (new)
- `docs/examples.md` (new)
- `docs/faq.md` (new)
- Update `README.md` with Phase 2 notes

**User Guide** (`docs/user_guide.md`):
- Installation (macOS, Linux, Windows via WSL)
- Quick start (5 min)
- Using the CLI:
  - `dash-ai ingest` — examples and options
  - `dash-ai ask` — query syntax, examples
  - `dash-ai chat` — interactive mode walkthrough
  - `dash-ai list` — viewing documents
  - `dash-ai delete` — removing documents
- JSON output format with examples
- Configuration (`config/settings.yaml`)
- Setting custom model names
- Environment overrides (`.env`)

**Troubleshooting** (`docs/troubleshooting.md`):
- "Ollama connection refused" — how to fix
- "Model not found" — how to download
- "Empty search results" — why and what to do
- "Out of memory" — chunking strategies
- "Slow performance" — optimization tips
- "Database locked" — file handling
- Windows/WSL-specific issues

**Examples** (`docs/examples.md`):
- Ingest personal notes
- Ask questions about code
- Ingest documentation
- Using `--json` for automation
- Interactive chatbot workflow
- Batch processing scripts

**FAQ** (`docs/faq.md`):
- Can I use this offline? → Yes, but model must be pre-downloaded
- Can I export my data? → Yes, `sqlite3 db.sqlite "SELECT * FROM documents"`
- How do I clear all documents? → `rm ~/.local/share/dash-ai/db.sqlite` (or configure path)
- Can I use a different model? → Yes, set `MODEL_NAME` in `config/settings.yaml`
- How large can documents be? → Tested up to 10MB, chunked automatically
- Can I integrate this with my app? → Yes, use `uv run` to invoke CLI or import as library

**Definition of Done:**
- User guide complete and clear
- Troubleshooting covers common issues
- Examples are copy-paste ready
- FAQ answers 10+ questions
- Documentation links from README
- No broken links

---

#### 2.8 Developer Documentation (3 hrs)

**Objective:** Help future contributors understand and extend the codebase.

**Files to Create/Modify:**
- `docs/architecture.md` (update if needed)
- `docs/contributing.md` (new)
- `docs/extending.md` (new)
- Code comments for complex logic

**Contributing Guide** (`docs/contributing.md`):
- Development setup (`uv sync`, Ollama installation)
- Running tests (`pytest`, coverage)
- Linting and formatting (`ruff`, `black` if used)
- Git workflow and commit messages
- Adding a new component (step-by-step)
- Pull request process
- Code review checklist

**Extending Guide** (`docs/extending.md`):
- Adding a new input format (e.g., PDF)
- Adding a new storage backend (e.g., PostgreSQL)
- Supporting a new LLM runtime (e.g., llama.cpp)
- Adding vector search support
- Writing custom retrieval strategies
- Each with code examples and tests

**Architecture Document** (`docs/architecture.md` update if needed):
- Component overview diagram (ASCII or link to image)
- Data flow (ingest → store → retrieve → answer)
- Interface contracts
- Error propagation
- Performance considerations

**Code Comments:**
- Add clarifying comments to complex logic
- Document non-obvious algorithms (e.g., chunking)
- Explain why, not what (code shows what)

**Definition of Done:**
- Contributing guide helps new contributors start
- Extending guide enables new feature additions
- Architecture clear and documented
- Code comments explain tricky parts
- Examples are correct and tested

---

### Testing Strategy for Phase 2

**Test Categories:**

1. **Error Handling Tests (10–15 tests)**
   - Each exception type raised correctly
   - Error messages helpful and accurate
   - Recovery suggestions present
   - Graceful degradation works

2. **Interactive Mode Tests (8–10 tests)**
   - Multi-turn conversation simulation
   - Input/output mocking
   - Session management
   - History tracking

3. **JSON Output Tests (6–8 tests)**
   - Valid JSON generated
   - Schema validation
   - Error responses include JSON
   - Timestamp formats correct

4. **Edge Cases Tests (12–15 tests)**
   - Empty database
   - Large files
   - Special characters
   - Network failures
   - Malformed input
   - Unicode handling
   - Concurrent access (if applicable)

5. **Performance Tests (4–6 tests)**
   - Ingestion throughput
   - Search latency
   - Memory baseline
   - Scaling (e.g., 1000 docs)

**Test Coverage Target:** 95%+
**Estimated Test Count:** 50–70 new tests
**Running Tests:** `pytest tests/ -v --cov=src/dash_ai --cov-report=html`

---

## Implementation Order

**Week 3:**
1. Start: 2.1 (Enhanced error handling) — foundation for all subsequent work
2. Continue: 2.2 (Interactive mode) — builds on error handling
3. Continue: 2.3 (JSON output) — orthogonal feature
4. Finish: 2.4 (Progress indicators) — UI polish

**Week 4:**
1. Start: 2.5 (Comprehensive tests) — cover all new features and edge cases
2. Continue: 2.6 (Performance profiling) — baseline measurements
3. Finish: 2.7 & 2.8 (Documentation) — consolidate learning

---

## Deliverable

**After Phase 2:**

```
✅ Production-ready CLI tool with:
  • Robust error handling and helpful messages
  • Interactive multi-turn conversation mode
  • JSON output for automation
  • Progress indicators and timing info
  • 95%+ test coverage
  • Comprehensive user and developer docs
  • Profiled performance
  • Edge cases handled gracefully
```

**README updates:**
- Add Phase 2 features to quick start
- Link to user guide and troubleshooting
- Document new `--json` flag and `chat` command
- Add performance benchmarks

---

## Notes

- **Backwards compatibility:** All Phase 2 changes are additive; Phase 1 CLI still works
- **Testing:** New tests should maintain fast execution (< 5s for full suite)
- **Documentation:** Focus on clarity for non-expert users
- **Performance:** Aim to keep typical operations under 2 seconds
- **Error messages:** Always suggest a recovery action (e.g., "Is Ollama running?")

---

## Success Metrics

By end of Phase 2:

- ✅ All Phase 1 tests pass (87/87)
- ✅ 50–70 new Phase 2 tests pass
- ✅ Code coverage ≥ 95%
- ✅ Interactive mode demo works
- ✅ JSON output tested and documented
- ✅ User guide helps newcomers in < 10 minutes
- ✅ Performance baseline established
- ✅ No user-facing error tracebacks
- ✅ System works offline (after model download)
- ✅ Ready for Phase 3 (extensibility)

---

**Estimated Effort:** 30–40 hours
**Target Completion:** End of Week 4
