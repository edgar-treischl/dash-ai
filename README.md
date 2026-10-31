# Local AI — Project Summary & Development Plan

## Quick start

Run commands from the repository root. On macOS with Homebrew:

```bash
brew install uv ollama
make install
```

Ollama is a separate system application; `uv sync` does not install it.
On Linux, install [uv](https://docs.astral.sh/uv/getting-started/installation/),
[Ollama](https://ollama.com/download), and `make` first.

In terminal 1, start the local model server and leave it running:

```bash
make start
```

In terminal 2, download the configured model and use the application:

```bash
make pull
make ingest
make ask QUESTION="What is this project about?"
make list
```

`make pull` reads the model name from `config/settings.yaml` (default: `mistral`,
overridable with `MODEL_NAME`). Download it once; subsequent sessions only need
the server running. All CLI commands currently require Ollama and the configured
model, including ingestion and listing.

Import your own Markdown file or recursively import a directory:

```bash
make ingest INPUT="path/to/notes.md"
make ingest INPUT="path/to/notes"
make ask QUESTION="What do my notes say about Python?"
```

Make targets use `uv run`, so activating `.venv` is unnecessary. Use `make help`
for targets, `make install-dev` for development dependencies, and `make test`
to run tests. See the [Quick Start guide](docs/guides/quickstart.md) for direct CLI
commands and troubleshooting.

## 1. Project vision

Build a **local-first AI knowledge assistant** in Python that can answer questions based on information provided through external data sources, starting with Markdown files.

The project should begin small and simple but have a modular architecture that allows us to expand it over time.

The long-term objective is to develop an independent AI platform that can:

- Understand and process different types of input.
- Build knowledge from user-provided information.
- Answer questions based on that knowledge.
- Distinguish between provided information and its pretrained knowledge.
- Support different local AI models.
- Eventually support custom training and fine-tuning.
- Run locally on a computer or later inside a VM.

## 2. Core design principles

| Principle | Decision |
|---|---|
| Local-first | No cloud AI dependencies |
| Programming language | Python |
| Architecture | Modular and extensible |
| Initial complexity | Keep it simple |
| Model independence | Support interchangeable models |
| Input independence | Support interchangeable input formats |
| Data privacy | Data remains locally stored |
| Development | Incremental, testable and documented |
| Deployment | Initially local, eventually VM-compatible |

**Important architectural decision:** The application must not be tightly coupled to any particular AI model, input format, or storage implementation.

## 3. Initial technology stack

| Component | Technology |
|---|---|
| Programming language | Python |
| Package/environment manager | uv |
| Local model runtime | Ollama |
| Initial language model | Small 3B–4B instruct model |
| Initial input | Markdown |
| Knowledge storage | SQLite |
| Initial search | Full-text search |
| Interface | CLI |
| Testing | pytest |
| Configuration | YAML |

### Hardware

Initial development machine:

- Apple M5 Pro
- 24 GB RAM
- macOS

Future deployment target:

- Virtual machine
- Linux-compatible environment
- Local model execution

We should avoid hardware-specific application logic so that the project can move between environments.

## 4. How the system will work

The initial architecture follows this workflow:

```text
                  USER
                   |
                   v
              CLI INTERFACE
                   |
                   v
             QUESTION ENGINE
                   |
                   v
           KNOWLEDGE RETRIEVAL
                   |
                   v
              SQLITE STORAGE
                   |
                   v
           RELEVANT INFORMATION
                   |
                   v
              LOCAL LLM
                   |
                   v
             GENERATED ANSWER
                   |
                   v
                  USER
```

Knowledge ingestion

Markdown documents will be imported into the knowledge system.

```text
Markdown Files
      |
      v
  Markdown Reader
      |
      v
  Text Processing
      |
      v
  Document Storage
      |
      v
  Search Index
```

## 5. Question answering

When a user asks a question:
1. The system receives the question.
2. The knowledge engine searches for relevant information (top-k=5 documents).
3. Relevant document sections are retrieved via full-text search (SQLite FTS5).
4. The question and retrieved information are sent to the local model.
5. The model generates an answer.
6. The answer includes references to the source documents.

This approach is called RAG (Retrieval-Augmented Generation).

## 6. Implementation Details

### 6.1 Chunking Strategy

Documents are split into chunks to balance context relevance and size:

- **Method:** Paragraph-based splitting
  - Split Markdown by `\n\n` (paragraph boundaries)
  - Combine paragraphs until reaching ~500 characters
  - Store chunk index in metadata for source tracking
- **Rationale:** Simple, works well for Markdown, preserves semantic boundaries, improvable in Phase 3 (token-based or overlapping chunks)

### 6.2 CLI Commands

The application provides four core commands:

```bash
# Ingest Markdown files from a directory
dash-ai ingest <directory-or-file-path>

# Ask a question and retrieve an answer with sources
dash-ai ask "<question>"

# List all imported documents with metadata
dash-ai list

# Delete a document by ID
dash-ai delete <document-id>

# Show help
dash-ai --help
```

**Design:** One-shot mode initially (Phase 1); interactive mode deferred to Phase 2.

### 6.3 Retrieval Strategy

- **Search method:** SQLite FTS5 (full-text search with BM25-like ranking)
- **Top-k:** Retrieve 5 most relevant documents per query
- **Scoring:** SQLite FTS5 built-in scoring (0.0 to 1.0 normalized relevance)
- **Filtering:** No metadata filtering in Phase 1; ready for advanced filtering in Phase 2+
- **Preparation for Phase 3:** Schema designed to support vector search integration without refactoring

### 6.4 Context Window Management

- **Assumed context size:** 4K tokens for initial model (mistral 7B)
- **Prompt structure:**
  ```
  Based on the following information:
  
  [Retrieved document content]
  
  Answer this question: [User question]
  ```
- **Overflow handling:**
  - If total prompt + question exceeds 3500 tokens, truncate retrieved documents (keep highest-scoring chunks first)
  - Future (Phase 2+): Implement smarter summarization or hierarchical retrieval
- **Model configuration:** Set via `config/settings.yaml`; easily swappable for different context sizes

### 6.5 Error Handling Strategy (Phase 1)

- **Ollama connection failures:** Retry up to 3 times with exponential backoff; fail gracefully with clear error message
- **Inference timeouts:** 30-second timeout; inform user if model is slow
- **Partial ingestion failures:** Continue ingesting valid files; report failed files at end
- **Configuration errors:** Validate on startup; suggest fixes for missing/invalid settings

### 6.6 Testing Approach (Phase 1)

- **Unit tests:** Mocked dependencies (mock Ollama, mocked storage)
  - Config loading and validation
  - Markdown parsing and chunking
  - Storage CRUD operations
  - FTS search scoring
  - CLI argument parsing
  - Prompt building
- **Integration tests:** Real SQLite + mocked Ollama
  - End-to-end ingestion workflow
  - Full-text search accuracy
  - Answer generation with source references
- **Coverage target:** 70%+ for Phase 1
- **Test data:** Fixtures with sample Markdown files in `tests/fixtures/`


## 7. Implementation Phases

The development is organized into three phases:

### Phase 1: Foundation & Core Loop (Weeks 1–2)
**Goal:** Get end-to-end RAG working. Users can ask questions on Markdown docs and get answers with source references.

- Project setup and core interfaces
- Configuration management
- Markdown ingestion with chunking
- SQLite storage with full-text search
- Ollama integration
- Retrieval engine
- Question-answering orchestration
- CLI with basic commands
- Application layer
- Entry point and tests

**Deliverable:** End-to-end RAG functioning. Run `dash-ai ingest`, then `dash-ai ask "<question>"` and receive answers with sources.

See `PHASE_1_PLAN.md` for detailed task breakdown.

### Phase 2: Polish & Robustness (Weeks 3–4)
- Enhanced error handling and resilience
- Interactive CLI mode
- Advanced CLI features (JSON output, progress indicators)
- Comprehensive test coverage
- Performance tuning and profiling
- Expanded documentation (user guide, troubleshooting, developer guide)

**Deliverable:** Production-ready CLI tool with robust error handling and excellent UX.

### Phase 3: Extensibility & Performance (Weeks 5+)
- Multiple input formats (PDF, TXT, CSV, JSON)
- Alternative storage backends (PostgreSQL, vector databases)
- Alternative LLM runtimes (llama.cpp, MLX for Apple Silicon)
- Advanced retrieval (vector search, hybrid search, metadata filtering)
- Custom training and fine-tuning infrastructure

**Deliverable:** Pluggable system supporting diverse data sources, storage options, and inference engines.

## 8. Initial repository structure

```text
dash-ai/
│
├── README.md
├── PHASE_1_PLAN.md
├── pyproject.toml
├── .gitignore
│
├── config/
│   └── settings.yaml
│
├── data/
│   └── knowledge/
│       └── example.md
│
├── src/
│   └── dash_ai/
│       │
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── app.py
│       │
│       ├── core/
│       │   ├── __init__.py
│       │   ├── config.py
│       │   └── interfaces.py
│       │
│       ├── ingestion/
│       │   ├── __init__.py
│       │   └── markdown.py
│       │
│       ├── knowledge/
│       │   ├── __init__.py
│       │   ├── document.py
│       │   └── storage.py
│       │
│       ├── models/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   └── ollama.py
│       │
│       └── answering/
│           ├── __init__.py
│           ├── retrieval.py
│           └── engine.py
│
├── tests/
│   ├── __init__.py
│   ├── fixtures/
│   │   └── sample.md
│   ├── test_config.py
│   ├── test_interfaces.py
│   ├── test_ingestion.py
│   ├── test_storage.py
│   ├── test_ollama.py
│   ├── test_retrieval.py
│   ├── test_answering.py
│   ├── test_cli.py
│   └── test_app.py
│
├── docs/
│   ├── architecture.md
│   ├── development.md
│   └── roadmap.md
│
└── .github/
    └── copilot-instructions.md
```

## 9. Architecture and modularity

The application should be designed around independent components with clearly defined responsibilities.

The goal is to make it possible to replace or extend individual components without having to rewrite the entire application.

We will focus on three main architectural areas:

### 9.1 Model interface

The application should communicate with an abstract model interface rather than directly with a specific AI runtime.

This allows us to change the underlying model or inference engine without changing the rest of the application.

**Initial implementation:**
- Ollama

**Potential future implementations:**
- llama.cpp
- MLX (Apple Silicon)
- Other local inference engines
- Custom models

The model interface should initially support:
- Sending prompts.
- Receiving generated responses.
- Configuring the selected model.
- Handling connection and inference errors.
- Supporting streaming responses in the future.

### 9.2 Input interface

The ingestion system should support different input formats through independent readers.

Each reader is responsible for converting its specific input format into a common internal document representation.

**Initial implementation:**
- Markdown

**Potential future additions:**
- TXT
- PDF
- DOCX
- CSV
- JSON
- SQL databases
- APIs

All input formats should eventually produce a standardized document structure.

This ensures that the knowledge processing and answering components do not need to know where the information originally came from.

### 9.3 Storage interface

The knowledge storage layer should be independent of the input format and AI model.

**Initial implementation:**
- SQLite

**Potential future additions:**
- PostgreSQL
- Vector databases
- Other local storage solutions

The storage layer should initially support:
- Saving documents.
- Retrieving documents.
- Updating existing documents.
- Removing documents.
- Tracking document metadata.
- Searching document content.

We should only introduce alternative storage technologies when there is a concrete need.

### 9.4 Common internal document representation

All imported information should be converted into a common document structure.

For example:

```python
Document(
    id="unique-document-id",
    title="Example Document",
    content="Document content...",
    source="example.md",
    format="markdown",
    metadata={},
)
```

This creates a consistent interface between ingestion, processing, storage, and retrieval.


### 9.5 Separation of responsibilities

The application should consist of independent components, each responsible for a clearly defined part of the system.

The goal is to keep business logic, data processing, storage, and AI inference separate.

This makes the application easier to maintain, test, extend, and eventually deploy in different environments.

#### Initial component structure

```text
CLI
 |
 v
Application Layer
 |
 +---------------------+
 |                     |
 v                     v
Ingestion          Answering
 |                     |
 v                     v
Document             Retrieval
Processing              |
 |                      v
 v                   Knowledge
Knowledge               Storage
Storage                  |
                         v
                     Model Interface
                         |
                         v
                     Local LLM
```


#### Component responsibilities

**1. CLI**
- Provides the user interface.
- Accepts commands and questions.
- Displays results and errors.
- Does not contain business logic.

**2. Application Layer**
- Coordinates application workflows.
- Connects the CLI with the underlying components.
- Manages application-level operations.
- Keeps individual components independent.

**3. Ingestion**
- Discovers input files.
- Selects the appropriate input reader.
- Converts input into a common document representation.
- Passes processed documents to the knowledge storage layer.

**4. Document Processing**
- Normalizes document content.
- Splits documents into smaller sections when required.
- Extracts relevant metadata.
- Prepares documents for indexing and retrieval.

**5. Knowledge Storage**
- Persists documents and metadata.
- Provides document retrieval and search capabilities.
- Handles updates and deletions.
- Hides the underlying storage implementation.

**6. Answering**
- Receives user questions.
- Coordinates knowledge retrieval and model inference.
- Builds the context required for answering.
- Processes and returns generated answers.

**7. Retrieval**
- Searches the knowledge base.
- Identifies relevant document sections.
- Returns relevant information with source references.
- Remains independent of the language model.

**8. Model Interface**
- Defines a common interface for AI models.
- Handles prompt submission and response generation.
- Provides model configuration and error handling.
- Allows different inference engines to be integrated.

**9. Local LLM**
- Executes the actual language model.
- Interprets prompts and provided context.
- Generates responses.
- Does not manage documents or knowledge storage.