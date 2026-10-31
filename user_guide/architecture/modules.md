# Module Structure

Overview of code organization and key files.

## Package Hierarchy

```
src/dash_ai/
├── __init__.py              # Package initialization
├── __main__.py              # Entry point: python -m dash_ai
├── cli.py                   # Command-line interface
├── app.py                   # Application orchestration layer
├── core/
│   ├── __init__.py
│   ├── interfaces.py        # Abstract base classes & protocols
│   └── config.py            # Configuration management
├── ingestion/
│   ├── __init__.py
│   └── markdown.py          # Markdown file reader & chunker
├── knowledge/
│   ├── __init__.py
│   └── storage.py           # SQLite storage backend
├── models/
│   ├── __init__.py
│   └── ollama.py            # Ollama LLM integration
└── answering/
    ├── __init__.py
    ├── retrieval.py         # Full-text search retrieval
    └── engine.py            # RAG question-answering engine
```

## Core Modules

### `__init__.py`
Exports public API:
```python
from .app import App
from .core.interfaces import Document
from .core.config import Config
```

### `__main__.py`
Entry point supporting both:
- `python -m dash_ai`
- `dash-ai` (console script via pyproject.toml)

Routes to CLI main function.

### `cli.py` (220 lines)
**Responsibility:** User-facing command interface

**Public Classes:**
- `CLI` — Command parser and dispatcher

**Public Functions:**
- `main()` — Entry point for CLI

**Commands:**
| Command | Purpose | Example |
|---------|---------|---------|
| `ingest` | Add documents to knowledge base | `dash-ai ingest file.md` |
| `ask` | Query knowledge base | `dash-ai ask "What is this?"` |
| `list` | Show ingested documents | `dash-ai list` |
| `delete` | Remove a document | `dash-ai delete file.md` |

**Error Handling:**
- User-friendly messages
- Suggests recovery actions
- No stack traces (caught at CLI level)

### `app.py` (140 lines)
**Responsibility:** Orchestration layer coordinating all components

**Public Classes:**
- `App` — Main application class

**Key Methods:**
```python
App.__init__(config: Config)
App.ingest_files(file_paths: list[str]) -> None
App.ask_question(question: str) -> str
App.list_documents() -> list[Document]
App.delete_document(source: str) -> None
```

**Workflow:**
1. Loads Config from YAML + env overrides
2. Initializes Model, Storage, Retriever, AnsweringEngine
3. Coordinates high-level workflows
4. Error handling and logging

**No business logic** — delegates to component modules.

## Core Package

### `core/interfaces.py` (180 lines)
**Responsibility:** Define abstract contracts for all pluggable components

**Public Classes:**
- `Document` — Data class for standardized document format
- `ModelInterface` — Abstract base for LLM providers
- `ReaderInterface` — Abstract base for input format handlers
- `StorageInterface` — Abstract base for persistence backends
- `RetrievalInterface` — Abstract base for search engines

**Design Pattern:** All components implement one of these interfaces, enabling:
- Multiple implementations per interface
- Easy testing with mocks
- Loose coupling between components

**Example — Adding a new LLM provider:**
```python
class MyModelProvider(ModelInterface):
    def generate(self, prompt: str) -> str:
        # Custom implementation
        pass

# Use in App via config:
# model:
#   provider: "my_provider"
```

### `core/config.py` (120 lines)
**Responsibility:** Load and manage configuration from YAML + environment

**Public Classes:**
- `Config` — Configuration container

**Public Methods:**
```python
Config.load(config_path: str) -> Config
Config.load_with_env() -> Config
```

**Configuration Sources (priority):**
1. Environment variables (via `.env` file)
2. YAML file (`config/settings.yaml`)
3. Built-in defaults

**Example:**
```python
config = Config.load_with_env()
print(config.model.model_name)  # "mistral" or from env override
print(config.storage.path)       # database path
```

## Ingestion Package

### `ingestion/markdown.py` (120 lines)
**Responsibility:** Parse and chunk Markdown files

**Public Classes:**
- `MarkdownReader` — Implements `ReaderInterface`

**Key Method:**
```python
def read_file(file_path: str) -> list[Document]
    # Returns list of Document objects, one per paragraph
    # Chunk size: ~500 characters (configurable)
    # Includes metadata: source file, chunk index, title
```

**Chunking Algorithm:**
1. Read entire file
2. Split by paragraph (double newline `\n\n`)
3. Filter empty paragraphs
4. Create chunk-sized groups
5. Generate unique IDs: `{filename}_{chunk_index}`

**Metadata Tracking:**
- `source` — Original file path
- `chunk_index` — Position in document
- `title` — Document title (from first chunk)

## Knowledge Package

### `knowledge/storage.py` (280 lines)
**Responsibility:** Persist and search documents using SQLite

**Public Classes:**
- `SQLiteStorage` — Implements `StorageInterface`

**Key Methods:**
```python
def save_document(doc: Document) -> None
def get_document(doc_id: str) -> Document
def list_documents() -> list[Document]
def delete_document(doc_id: str) -> None
def search(query: str, top_k: int, min_score: float) -> list[tuple[Document, float]]
```

**Database Schema:**
- Table `documents` — Document storage with metadata (JSON)
- Virtual table `documents_fts` — FTS5 full-text search index

**Search Features:**
- Full-text search across title, content, source
- Relevance scoring (0.0-1.0)
- Configurable result limits and min score
- Query escaping for special characters

**Critical Implementation Detail:**
FTS5 doesn't support parameterized MATCH expressions, so:
```python
# Query escaping: wrap in quotes, double internal quotes
escaped = f'"{query.replace('"', '""')}"'
# Result: "user?query" → normalized phrase search
```

## Models Package

### `models/ollama.py` (160 lines)
**Responsibility:** Interface with local Ollama language model

**Public Classes:**
- `OllamaModel` — Implements `ModelInterface`

**Key Methods:**
```python
def generate(prompt: str) -> str
    # Sends prompt to Ollama
    # Returns AI-generated response
    # Retries on connection failure with exponential backoff
```

**Features:**
- HTTP client to Ollama API
- Connection verification on init
- Retry logic with exponential backoff (1s, 2s, 4s delays)
- 30-second request timeout
- User-friendly error messages

**Configuration:**
```yaml
model:
  host: "localhost"
  port: 11434
  model_name: "mistral"
  timeout: 30
  retry_attempts: 3
  retry_delay: 1
```

## Answering Package

### `answering/retrieval.py` (90 lines)
**Responsibility:** Retrieve relevant documents for a query

**Public Classes:**
- `Retriever` — Implements `RetrievalInterface`

**Key Method:**
```python
def retrieve(query: str, top_k: int = 5) -> list[tuple[Document, float]]
    # Returns top-k most relevant documents with scores (0.0-1.0)
    # Delegates to storage backend for search
```

**Scoring:**
- Uses storage's FTS5 relevance scores
- Normalizes to 0.0-1.0 range
- Higher score = more relevant

### `answering/engine.py` (100 lines)
**Responsibility:** Implement RAG pipeline combining retrieval + generation

**Public Classes:**
- `AnsweringEngine` — Orchestrates retrieval and model generation

**Key Method:**
```python
def answer(question: str) -> str
    # 1. Retrieve relevant documents
    # 2. Build prompt from context
    # 3. Generate answer from model
    # 4. Add source attribution
```

**Prompt Format:**
```
You are a helpful assistant. Answer based on the provided context.

Context:
[Retrieved document chunks]

Question: [User question]

Answer: [Generated response]
```

**Source Attribution:**
Appends to response:
```
Sources:
- file.md (chunk 1): [excerpt]
- file.md (chunk 3): [excerpt]
```

## Test Structure

### `tests/conftest.py`
Pytest fixtures for all tests:
- `temp_db` — Temporary SQLite database
- `sample_document` — Single test document
- `sample_documents` — Multiple test documents
- `mock_ollama` — Mocked Ollama responses
- `sample_config` — Test configuration

### Test Modules (9 files, 79 tests)
| Module | Tests | Purpose |
|--------|-------|---------|
| `test_interfaces.py` | 5 | Document, abstract classes |
| `test_config.py` | 6 | YAML loading, validation |
| `test_ingestion.py` | 8 | Markdown parsing, chunking |
| `test_storage.py` | 14 | CRUD, search, persistence |
| `test_ollama.py` | 10 | Connection, retry, errors |
| `test_retrieval.py` | 6 | Document retrieval |
| `test_answering.py` | 7 | RAG pipeline |
| `test_cli.py` | 11 | Command interface |
| `test_app.py` | 13 | Orchestration |

## Key Architectural Patterns

### 1. Dependency Injection
Components receive dependencies via constructor:
```python
class AnsweringEngine:
    def __init__(self, retriever: Retriever, model: ModelInterface):
        self.retriever = retriever
        self.model = model
```

### 2. Strategy Pattern
Multiple implementations of same interface:
- `ModelInterface` — `OllamaModel`, future `LlamaCppModel`, etc.
- `StorageInterface` — `SQLiteStorage`, future `PostgresStorage`, etc.
- `ReaderInterface` — `MarkdownReader`, future `PDFReader`, etc.

### 3. Facade Pattern
`App` class hides complexity of component coordination:
```python
app.ingest_files(["doc1.md", "doc2.md"])  # Simple interface
# App internally: coordinates Reader → Storage → Indexing
```

### 4. Configuration as Dependency
Config object injected into components instead of hardcoding:
```python
class OllamaModel:
    def __init__(self, config: ModelConfig):
        self.host = config.host  # No hardcoded "localhost"
```

## File Size Reference

| File | Lines | Purpose |
|------|-------|---------|
| `cli.py` | 220 | CLI commands and parsing |
| `app.py` | 140 | Application orchestration |
| `storage.py` | 280 | Database operations |
| `config.py` | 120 | Configuration management |
| `interfaces.py` | 180 | Abstract base classes |
| `markdown.py` | 120 | Markdown reader |
| `ollama.py` | 160 | LLM integration |
| `retrieval.py` | 90 | Document retrieval |
| `engine.py` | 100 | RAG pipeline |

**Total: ~1,200 lines of core code**

## Adding a New Component

**Example: Add PDF ingestion**

1. Create `ingestion/pdf.py`:
```python
from core.interfaces import ReaderInterface, Document

class PDFReader(ReaderInterface):
    def read_file(self, path: str) -> list[Document]:
        # PDF parsing logic
        pass
```

2. Update config:
```yaml
ingestion:
  reader: "pdf"  # instead of "markdown"
```

3. Update `App.__init__()` to instantiate based on config

4. Write tests in `tests/test_pdf.py`

**No changes needed to CLI, storage, or model layers.**

## Key Files to Know

| File | Why Important | When to Edit |
|------|---------------|--------------|
| `cli.py` | User interface | Adding new commands |
| `app.py` | Orchestration | Adding new workflows |
| `interfaces.py` | Component contracts | Adding new component types |
| `config.py` | Settings management | Adding new config sections |
| `storage.py` | Data persistence | Changing search strategy |
| `ollama.py` | LLM integration | Changing model provider |
| `engine.py` | Answer generation | Changing prompt format |

