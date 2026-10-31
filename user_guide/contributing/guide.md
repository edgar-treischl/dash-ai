# Contributing Guide

How to develop and contribute to dash-ai.

## Getting Started

### Prerequisites
- Python 3.10+
- `uv` package manager
- Git
- Ollama (for testing with real models)

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/edgar-treischl/dash-ai.git
cd dash-ai

# Install application and test dependencies
make install-dev

# Verify installation
uv run dash-ai --help
```

## Project Structure

```
dash-ai/
├── src/dash_ai/          # Source code
├── tests/                # Test suite
├── docs/                 # Documentation
├── config/               # Configuration templates
├── data/                 # Sample data
├── pyproject.toml        # Project metadata
└── README.md             # Project overview
```

## Development Workflow

### 1. Create a Feature Branch

```bash
# Update main branch
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/add-pdf-support
# or git checkout -b bugfix/fix-search-scoring
```

Branch naming:
- Feature: `feature/short-description`
- Bug fix: `bugfix/short-description`
- Documentation: `docs/short-description`

### 2. Make Changes

Edit code in `src/dash_ai/`:

```bash
# Example: Add new feature
vim src/dash_ai/ingestion/pdf.py

# Or edit existing module
vim src/dash_ai/models/ollama.py
```

### 3. Write Tests

Add tests in `tests/` mirroring source structure:

```bash
# Example: Test new PDF reader
vim tests/test_pdf.py

# Or test modifications
vim tests/test_ollama.py
```

### 4. Run Tests

```bash
# Run all tests
make test

# Run specific test file
uv run --extra dev pytest tests/test_pdf.py

# Run with coverage
uv run --extra dev pytest tests/ --cov=src/dash_ai

# Run with verbose output
uv run --extra dev pytest tests/ -vv
```

### 5. Update Documentation

Update relevant docs if changing behavior:

```bash
# Configuration changes?
vim docs/guides/configuration.md

# New feature?
vim docs/architecture/modules.md
vim docs/guides/quickstart.md

# New command?
vim docs/api/cli.md
```

### 6. Commit and Push

```bash
# Stage changes
git add src/ tests/ docs/

# Commit with descriptive message
git commit -m "Add PDF ingestion support

- Implement PDFReader class with text extraction
- Add tests for PDF parsing
- Update documentation with PDF configuration"

# Push to your fork
git push origin feature/add-pdf-support
```

Commit message guidelines:
- First line: Brief summary (50 chars max)
- Blank line
- Detailed description (wrap at 72 chars)
- Reference issues: "Closes #123"

### 7. Create Pull Request

Push to your fork and open PR on GitHub:
- Link related issues
- Describe changes clearly
- Reference any breaking changes

## Code Style & Conventions

### Python Style (PEP 8)

```bash
# Check style (if configured)
# Currently enforced via code review

# Use meaningful names
from dash_ai.models.ollama import OllamaModel  # ✓
from dash_ai.models.ollama import om           # ✗

# Use snake_case for functions/variables
def process_document(doc):  # ✓
def processDocument(doc):   # ✗

# Use PascalCase for classes
class DocumentProcessor:    # ✓
class document_processor:   # ✗

# Use UPPER_CASE for constants
MAX_CHUNK_SIZE = 500        # ✓
max_chunk_size = 500        # ✗
```

### Type Hints

Always include type hints:

```python
# ✓ With type hints
def search(query: str, top_k: int = 5) -> list[tuple[Document, float]]:
    """Search documents by full-text query."""
    pass

# ✗ Without type hints
def search(query, top_k=5):
    pass
```

### Docstrings

Use concise docstrings:

```python
def answer(question: str) -> str:
    """Generate answer to question using RAG pipeline.
    
    Retrieves relevant documents, builds prompt, generates response
    with source attribution.
    
    Args:
        question: User question to answer
        
    Returns:
        Answer with source references
        
    Raises:
        ValueError: If no documents ingested
        ConnectionError: If Ollama unavailable
    """
```

### Comments

Comment only non-obvious logic:

```python
# ✓ Helpful comment
# FTS5 doesn't support parameterized MATCH, so escape and format
escaped_query = f'"{query.replace('"', '""')}"'

# ✗ Obvious comment
# Get the value from config
value = config.value

# ✗ Outdated comment
# TODO: Remove this in phase 2  <- If not planned, don't add
```

### Imports

Organize imports in groups:

```python
# Standard library
import json
from pathlib import Path
from typing import Optional

# Third-party packages
import requests
import yaml

# Local packages
from dash_ai.core.interfaces import Document
from dash_ai.knowledge.storage import SQLiteStorage
```

## Testing Guidelines

### Test Coverage

- Minimum 70% (aim for 90%+)
- Unit tests for each component
- Integration tests for workflows
- Error case tests

### Test Naming

```python
# ✓ Descriptive name
def test_search_returns_documents_sorted_by_score():
    pass

# ✗ Vague name
def test_search():
    pass
```

### Test Structure (Arrange-Act-Assert)

```python
def test_save_document(temp_db):
    # Arrange
    storage = SQLiteStorage(temp_db)
    doc = Document(id="1", title="Test", content="Content", source="test.md")
    
    # Act
    storage.save_document(doc)
    result = storage.get_document("1")
    
    # Assert
    assert result.title == "Test"
```

### Running Tests Locally

```bash
# Before committing
pytest tests/                              # All tests
pytest tests/ --cov=src/dash_ai           # With coverage
pytest tests/ -x                           # Stop on first failure
```

## Git Workflow

### Before Starting Work

```bash
# Update from upstream
git fetch origin
git rebase origin/main

# Or if you've made local commits
git pull --rebase origin main
```

### During Development

```bash
# Check status
git status

# Stage changes
git add src/dash_ai/file.py
git add tests/test_file.py

# Commit frequently
git commit -m "Add feature part 1"
git commit -m "Add feature part 2"

# Keep main branch clean
git fetch origin
git rebase origin/main
```

### Before Pull Request

```bash
# Ensure tests pass
pytest tests/

# Check coverage
pytest tests/ --cov=src/dash_ai

# Rebase if main has new commits
git fetch origin
git rebase origin/main

# Push to your fork
git push origin feature/my-feature
```

## Common Development Tasks

### Adding a New Component

**Example: Add vector search (future feature)**

1. **Create interface** (if new type):
   ```python
   # src/dash_ai/core/interfaces.py
   class VectorRetrievalInterface(ABC):
       @abstractmethod
       def embed_and_search(self, query: str) -> list[Document]:
           pass
   ```

2. **Implement component**:
   ```python
   # src/dash_ai/retrieval/vector.py
   class VectorRetriever(VectorRetrievalInterface):
       def embed_and_search(self, query: str) -> list[Document]:
           # Implementation
           pass
   ```

3. **Write tests**:
   ```python
   # tests/test_vector_retrieval.py
   def test_vector_search(mock_embeddings):
       retriever = VectorRetriever(mock_embeddings)
       results = retriever.embed_and_search("query")
       assert len(results) > 0
   ```

4. **Update documentation**:
   - Add to `docs/architecture/modules.md`
   - Update `docs/guides/roadmap.md`

### Modifying Existing Component

**Example: Add streaming support to OllamaModel**

1. Check existing tests:
   ```bash
   grep -n "def test" tests/test_ollama.py
   ```

2. Update implementation:
   ```python
   # src/dash_ai/models/ollama.py
   class OllamaModel:
       def generate_stream(self, prompt: str):
           # Streaming implementation
           pass
   ```

3. Add tests:
   ```python
   # tests/test_ollama.py
   def test_streaming_response(mock_ollama):
       model = OllamaModel(mock_ollama)
       stream = model.generate_stream("prompt")
       for chunk in stream:
           assert isinstance(chunk, str)
   ```

4. Update documentation if behavior changes

### Fixing a Bug

1. Create failing test first:
   ```python
   # tests/test_storage.py
   def test_search_handles_special_characters():
       """Test that FTS5 search handles ? and * correctly."""
       storage = SQLiteStorage(temp_db)
       storage.save_document(Document(..., content="What? Why!"))
       
       # This should work without FTS5 syntax errors
       results = storage.search("What?")
       assert len(results) > 0
   ```

2. Fix the bug:
   ```python
   # src/dash_ai/knowledge/storage.py
   # Improve query escaping logic
   ```

3. Verify test passes:
   ```bash
   pytest tests/test_storage.py::test_search_handles_special_characters -vv
   ```

## Performance & Optimization

### Profiling

```bash
# Profile specific test
pytest tests/test_storage.py --durations=5

# Profile application
python -m cProfile -s cumulative -m dash_ai ask "query"
```

### Optimization Guidelines

- Profile before optimizing
- Don't optimize prematurely
- Focus on algorithmic improvements first
- Document performance decisions

## Documentation Updates

When changing functionality:

1. Update docstring in code
2. Update relevant guide (e.g., `docs/guides/quickstart.md`)
3. Update architecture docs if structure changes
4. Update roadmap if plans change

## Security Considerations

- Never commit secrets or credentials
- Use `.env` for sensitive configuration
- Sanitize user input before database queries
- Validate file paths (prevent traversal attacks)
- Review dependencies for known vulnerabilities

## Release Process

*Coming in Phase 2*

## Getting Help

- **Questions?** Open an issue with `question` label
- **Bug report?** Use `bug` label with reproduction steps
- **Feature request?** Use `enhancement` label
- **Documentation?** Use `documentation` label

## Code Review Checklist

Before requesting review:

- [ ] Tests pass locally: `pytest tests/`
- [ ] Coverage > 70%: `pytest --cov`
- [ ] No lint issues: Follow PEP 8
- [ ] Type hints complete
- [ ] Docstrings present
- [ ] Documentation updated
- [ ] Commit messages clear
- [ ] No sensitive data in code
- [ ] Related issues linked

## Contributor License Agreement

By contributing, you agree to:
- License contributions under MIT
- Original work (not copied code)
- Code follows project style
- Commits are your own work

## Recognition

Contributors will be recognized in:
- `CONTRIBUTORS.md` (if created)
- Commit messages
- GitHub insights

Thank you for contributing! 🎉
