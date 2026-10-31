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

## Task Breakdown

### WEEK 1: Setup & Interfaces

#### 1.1 Project Setup
**Files to create:**
- `pyproject.toml` — Project metadata and dependencies
- `.gitignore` — Ignore Python artifacts, SQLite, config secrets
- `config/settings.yaml` — Config template (Ollama, storage, retrieval settings)
- `.env.example` — Example environment variables
- Directory structure: `src/dash_ai/`, `tests/`, `data/knowledge/`, `docs/`

**Dependencies to add:**
```toml
dependencies = [
    "pyyaml>=6.0",
    "requests>=2.31",
    "python-dotenv>=1.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = "--strict-markers -ra"
```

**Definition of Done:**
- [ ] `uv sync` installs dependencies cleanly
- [ ] Directory structure matches README section 8
- [ ] Config template loads without errors
- [ ] `.env.example` documents all overridable settings

---

#### 1.2 Core Interfaces
**File:** `src/dash_ai/core/interfaces.py`

**Define these abstract base classes:**

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

@dataclass
class Document:
    """Common internal document representation."""
    id: str
    title: str
    content: str
    source: str  # "file.md"
    format: str  # "markdown"
    metadata: dict = field(default_factory=dict)


class ModelInterface(ABC):
    """Abstract interface for LLM models."""
    
    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate response from prompt."""
    
    @abstractmethod
    def get_model_name(self) -> str:
        """Return model identifier."""


class ReaderInterface(ABC):
    """Abstract interface for input format readers."""
    
    @abstractmethod
    def read(self, file_path: str) -> List[Document]:
        """Read file and return list of Document chunks."""
    
    @abstractmethod
    def supports_format(self, file_path: str) -> bool:
        """Check if reader handles this format."""


class StorageInterface(ABC):
    """Abstract interface for document storage."""
    
    @abstractmethod
    def save_document(self, doc: Document) -> None:
        """Save document to storage."""
    
    @abstractmethod
    def get_document(self, doc_id: str) -> Document:
        """Retrieve document by ID."""
    
    @abstractmethod
    def list_documents(self) -> List[Document]:
        """List all stored documents."""
    
    @abstractmethod
    def search(self, query: str, top_k: int = 5) -> List[Tuple[Document, float]]:
        """Full-text search. Return (Document, relevance_score) tuples."""
    
    @abstractmethod
    def delete_document(self, doc_id: str) -> None:
        """Delete document by ID."""


class RetrievalInterface(ABC):
    """Abstract interface for retrieval."""
    
    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5) -> List[Tuple[Document, float]]:
        """Retrieve relevant documents. Return (Document, score) tuples."""
```

**Definition of Done:**
- [ ] Interfaces defined with clear docstrings
- [ ] Type hints throughout
- [ ] `pytest tests/test_interfaces.py` passes (basic import test)

---

#### 1.3 Configuration Management
**File:** `src/dash_ai/core/config.py`

**Implement:**
- Load `config/settings.yaml` at startup
- Fall back to environment variables (e.g., `OLLAMA_HOST`)
- Validate required settings
- Raise clear errors if missing

**Config template (`config/settings.yaml`):**
```yaml
# Model configuration
model:
  type: ollama
  name: mistral
  host: http://localhost:11434

# Storage configuration
storage:
  type: sqlite
  path: ./data/knowledge.db

# Retrieval configuration
retrieval:
  top_k: 5
  min_relevance: 0.0

# Application settings
app:
  data_dir: ./data/knowledge/
  debug: false
```

**Definition of Done:**
- [ ] Config loads without errors
- [ ] Environment variable override works (e.g., `OLLAMA_HOST=http://127.0.0.1:11434`)
- [ ] Validation catches missing required fields with helpful error messages
- [ ] `pytest tests/test_config.py` passes

---

#### 1.4 Markdown Ingestion
**File:** `src/dash_ai/ingestion/markdown.py`

**Implement MarkdownReader:**
- Read Markdown files
- Extract title (from H1 or filename)
- Split into chunks using paragraph-based strategy (split by `\n\n`, combine until ~500 chars)
- Create Document objects with unique IDs
- Store chunk_index in metadata

**Algorithm:**
```python
def chunk_content(content: str, target_size: int = 500) -> List[str]:
    """Split content into chunks by paragraphs."""
    paragraphs = content.split('\n\n')
    chunks = []
    current_chunk = []
    current_size = 0
    
    for para in paragraphs:
        if current_size + len(para) > target_size and current_chunk:
            chunks.append('\n\n'.join(current_chunk))
            current_chunk = [para]
            current_size = len(para)
        else:
            current_chunk.append(para)
            current_size += len(para)
    
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))
    
    return chunks
```

**Definition of Done:**
- [ ] Reads Markdown files correctly
- [ ] Handles multiple files
- [ ] Generates unique Document IDs (e.g., `{filename}_{chunk_index}`)
- [ ] Stores chunk_index in metadata
- [ ] `pytest tests/test_ingestion.py::test_markdown_reader` passes

---

### WEEK 2: Storage, Inference, CLI

#### 1.5 SQLite Storage
**File:** `src/dash_ai/knowledge/storage.py`

**Implement SQLiteStorage:**

**Schema:**
```sql
CREATE TABLE documents (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  source TEXT NOT NULL,
  format TEXT NOT NULL,
  metadata TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE VIRTUAL TABLE documents_fts USING fts5(
  id,
  title,
  content,
  tokenize = 'porter'
);
```

**Implement methods:**
- `save_document(doc)` — Insert or update document and FTS index
- `get_document(doc_id)` — Retrieve by ID
- `list_documents()` — List all
- `search(query, top_k=5)` — FTS search with scoring
- `delete_document(doc_id)` — Delete by ID
- Schema auto-creation on first run

**Definition of Done:**
- [ ] Schema created automatically on first run
- [ ] CRUD operations work correctly
- [ ] FTS search returns results ranked by relevance (0.0 to 1.0)
- [ ] Database file created at configured path
- [ ] `pytest tests/test_storage.py` passes

---

#### 1.6 Ollama Integration
**File:** `src/dash_ai/models/ollama.py`

**Implement OllamaModel:**
- Connect to Ollama at configured host
- Send prompts to `POST /api/generate`
- Receive and parse responses
- Error handling:
  - Connection errors → retry up to 3 times with exponential backoff
  - Timeouts → 30-second limit with clear error
  - Model not found → helpful error message
- Retry logic with exponential backoff

**API Details:**
```
POST http://localhost:11434/api/generate
{
  "model": "mistral",
  "prompt": "...",
  "stream": false
}
→ {"response": "..."}
```

**Definition of Done:**
- [ ] Connects to running Ollama instance
- [ ] Generates responses correctly
- [ ] Handles errors gracefully (connection errors, timeouts, model not found)
- [ ] Retry logic works (exponential backoff)
- [ ] `pytest tests/test_ollama.py` passes (mocked HTTP)

---

#### 1.7 Retrieval Engine
**File:** `src/dash_ai/answering/retrieval.py`

**Implement Retriever:**
- Query storage for top_k relevant documents
- Return ranked list with source references
- Implement RetrievalInterface

**Definition of Done:**
- [ ] Retrieves relevant documents from storage
- [ ] Returns (Document, score) tuples
- [ ] Top-k parameter works (default 5)
- [ ] Scores are consistent and meaningful (0.0 to 1.0)
- [ ] `pytest tests/test_retrieval.py` passes

---

#### 1.8 Question-Answering Engine
**File:** `src/dash_ai/answering/engine.py`

**Implement AnsweringEngine:**
- Receive user question
- Call retriever → get top_k documents
- Build RAG prompt:
  ```
  Based on the following information:
  
  [Retrieved document content]
  
  Answer this question: [User question]
  ```
- Call model → get response
- Format answer with source references:
  ```
  Answer: [response]
  
  Sources:
  - [source 1] (chunk_index: x)
  - [source 2] (chunk_index: y)
  ```
- Return formatted answer

**Definition of Done:**
- [ ] End-to-end RAG works (retrieve → build prompt → model → format)
- [ ] Answer includes source references with document IDs and chunk indices
- [ ] Handles empty retrieval gracefully (inform user no relevant docs found)
- [ ] `pytest tests/test_answering.py` passes (mocked storage + model)

---

#### 1.9 CLI Interface
**File:** `src/dash_ai/cli.py`

**Implement commands:**

```bash
# Ingest Markdown files
dash-ai ingest <directory-or-file-path>
# Output: "Imported X documents with Y chunks"

# Ask a question
dash-ai ask "<question>"
# Output: Answer with sources

# List documents
dash-ai list
# Output: Formatted table of documents

# Delete a document
dash-ai delete <document-id>
# Output: "Deleted document X"

# Help
dash-ai --help
```

**Implementation details:**
- Use `argparse` for command parsing
- Separate command functions: `cmd_ingest()`, `cmd_ask()`, `cmd_list()`, `cmd_delete()`
- Call application layer (see 1.10)
- Format output clearly
- Exit with appropriate codes (0 = success, 1 = error)

**Definition of Done:**
- [ ] All commands work end-to-end
- [ ] Help text is clear and complete
- [ ] Error messages are user-friendly (e.g., "File not found: example.md")
- [ ] `pytest tests/test_cli.py` passes

---

#### 1.10 Application Layer
**File:** `src/dash_ai/app.py`

**Implement App class:**
- Initialize config, storage, models on startup
- High-level methods:
  - `ingest_files(path)` → calls ingestion + storage
  - `ask_question(query)` → calls retrieval + model + formatting
  - `list_documents()` → calls storage
  - `delete_document(doc_id)` → calls storage

**Key design:**
- CLI calls `App`, not components directly
- Components are loosely coupled (swappable)
- Config-based initialization (storage type, model type, etc.)

**Definition of Done:**
- [ ] Initializes all components from config
- [ ] CLI calls app methods, not components directly
- [ ] Components are swappable (could switch to different storage/model)
- [ ] `pytest tests/test_app.py` passes

---

#### 1.11 Entry Point
**File:** `src/dash_ai/__main__.py`

**Simple entry point:**
```python
import sys
from dash_ai.cli import main

if __name__ == '__main__':
    sys.exit(main())
```

**Also add to `pyproject.toml`:**
```toml
[project.scripts]
dash-ai = "dash_ai.cli:main"
```

**Definition of Done:**
- [ ] `python -m dash_ai ask "..."` works
- [ ] `dash-ai ask "..."` works (after `uv sync`)
- [ ] Handles top-level errors (config missing, Ollama not running, etc.)

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
