# Copilot Instructions for dash-ai

## Project Overview

**dash-ai** is a local-first AI knowledge assistant built in Python. It answers questions based on user-provided information (initially Markdown) using local language models (Ollama). No cloud AI dependencies.

The project emphasizes **modularity and extensibility**—components are loosely coupled to support future additions (PDF ingestion, different storage backends, alternative LLM runtimes).

## Technology Stack

| Component | Technology |
|---|---|
| Language | Python |
| Package/environment manager | uv |
| Local model runtime | Ollama |
| Storage | SQLite |
| Testing | pytest |
| Configuration | YAML |
| Initial input format | Markdown |
| Search | Full-text search |
| Interface | CLI |

### Hardware Target
- Apple M5 Pro (initial development)
- Linux-compatible VM (future deployment)

## Architecture & Design Principles

### Core Principle
**Do not tightly couple the application to any AI model, input format, or storage implementation.**

### System Workflow
```
User Question → CLI → Question Engine → Knowledge Retrieval → 
SQLite Storage → Local LLM (Ollama) → Generated Answer (with source references)
```

### Knowledge Ingestion
```
Markdown Files → Markdown Reader → Text Processing → 
SQLite Storage → Full-Text Search Index
```

### Component Structure

The application is divided into independent, testable components:

1. **CLI** — User interface; accepts commands/questions; no business logic
2. **Application Layer** — Coordinates workflows; keeps components independent
3. **Ingestion** — Converts input (Markdown → common document format); pluggable readers
4. **Knowledge Storage** — SQLite persistence; document retrieval; search interface
5. **Retrieval** — Full-text search; returns relevant sections with source references
6. **Answering Engine** — Orchestrates retrieval + LLM inference; builds context
7. **Model Interface** — Abstract interface for AI models (Ollama initially); allows swapping
8. **Local LLM** — Executes language model; does not manage documents

### Common Document Representation

All inputs convert to a standardized internal format:
```python
Document(
    id="unique-id",
    title="Title",
    content="Content...",
    source="file.md",
    format="markdown",
    metadata={},
)
```

This ensures ingestion, storage, retrieval, and inference remain independent.

## Initial Repository Structure (Target)

```
dash-ai/
├── README.md
├── pyproject.toml
├── .gitignore
├── config/
│   └── settings.yaml
├── data/
│   └── knowledge/
│       └── example.md
├── src/
│   └── dash_ai/
│       ├── __init__.py
│       ├── cli.py
│       ├── core/
│       │   ├── config.py
│       │   └── interfaces.py
│       ├── ingestion/
│       │   └── markdown.py
│       ├── knowledge/
│       │   ├── document.py
│       │   └── storage.py
│       ├── models/
│       │   ├── base.py
│       │   └── ollama.py
│       └── answering/
│           └── engine.py
├── tests/
│   ├── test_ingestion.py
│   ├── test_storage.py
│   └── test_answering.py
└── docs/
    ├── architecture.md
    ├── roadmap.md
    └── development.md
```

## Code Conventions

### Module Organization
- **Interfaces** (`core/interfaces.py`): Define abstract base classes/protocols for pluggable components (Model, Reader, Storage).
- **Implementations**: Each technology has its own module (e.g., `models/ollama.py`, `ingestion/markdown.py`).
- **No hardcoding**: Always use dependency injection or configuration to select implementations.

### Naming
- Use snake_case for functions and variables.
- Use PascalCase for classes.
- Use UPPER_CASE for constants.

### Interfaces & Protocols
Define interfaces early to enable different implementations later:
```python
from abc import ABC, abstractmethod

class ModelInterface(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        pass

class StorageInterface(ABC):
    @abstractmethod
    def save_document(self, doc: Document) -> None:
        pass
```

### Configuration
Use YAML config files in `config/settings.yaml` for:
- Ollama connection parameters
- Storage backend selection
- Search engine settings
- Model name and parameters

Load via `core/config.py`.

### Testing
- Use pytest; place tests in `tests/` mirroring source structure.
- Test each component in isolation; mock external dependencies.
- Example: test markdown ingestion without touching storage.
- Run single test: `pytest tests/test_ingestion.py::test_parse_markdown`
- Run all: `pytest`

## Development Workflow

### Setup
```bash
# Install uv if needed
# Create virtual environment and install dependencies
uv sync

# Ensure Ollama is running
ollama serve
```

### Testing
```bash
# Run all tests
pytest

# Run a specific test file
pytest tests/test_ingestion.py

# Run a specific test function
pytest tests/test_ingestion.py::test_parse_markdown

# Run with coverage
pytest --cov=src/dash_ai
```

### Code Style
- Use meaningful names (classes, functions, variables).
- Keep functions focused (single responsibility).
- Document non-obvious logic; avoid over-commenting.
- Use type hints throughout.

## Future Extensibility

The modular design supports these additions without major refactoring:

- **New input formats**: Create `ingestion/pdf.py`, `ingestion/csv.py`, etc.; implement `Reader` interface.
- **New storage backends**: Create `knowledge/postgres.py`; implement `StorageInterface`.
- **New LLM runtimes**: Create `models/llama_cpp.py` or `models/mlx.py`; implement `ModelInterface`.
- **Vector search**: Add `retrieval/vector_search.py`; implement `Retrieval` interface alongside full-text search.
- **Custom training**: Add `training/` module; keep independent of core components.

## Key Files to Know

- **README.md** — Project vision, design principles, architecture overview.
- **pyproject.toml** — Dependencies, build config, entry points (once created).
- **config/settings.yaml** — Ollama connection, model selection, storage backend.
- **core/interfaces.py** — Abstract base classes/protocols for all pluggable components.
- **ingestion/markdown.py** — Markdown reader implementation.
- **models/ollama.py** — Ollama LLM implementation.
- **knowledge/storage.py** — SQLite storage implementation.
- **answering/engine.py** — Question-answering orchestration.

## Common Patterns

### Adding a New Input Format
1. Create `ingestion/new_format.py`.
2. Implement `Reader` interface from `core/interfaces.py`.
3. Test with pytest; add tests to `tests/test_ingestion.py`.
4. Update ingestion dispatcher to recognize new format.

### Adding a New Storage Backend
1. Create `knowledge/new_backend.py`.
2. Implement `StorageInterface` from `core/interfaces.py`.
3. Update `core/config.py` to select backend via configuration.
4. Test with mocked LLM and ingestion.

### Adding Model Support
1. Create `models/new_model.py`.
2. Implement `ModelInterface` from `core/interfaces.py`.
3. Configure via `config/settings.yaml`.
4. Test answering engine with new model.

## Data Privacy & Deployment

- All data remains locally stored; no cloud uploads.
- Future VM deployment should use same code with Linux-compatible paths.
- Avoid hardcoding file paths; use `config/settings.yaml`.
- Keep model interface abstract to support different inference engines.

## Questions or Edge Cases

- **Version compatibility**: Target Python 3.10+.
- **Ollama dependencies**: Document required setup; provide easy setup instructions.
- **Search performance**: Start with SQLite full-text search; profile before optimizing.
- **Streaming responses**: Model interface is designed to support this; implement only if needed.
