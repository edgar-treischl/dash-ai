# Testing Guide

Write and run tests for dash-ai.

## Quick Start

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_storage.py

# Run specific test function
pytest tests/test_storage.py::test_save_and_retrieve_document

# Run with coverage report
pytest tests/ --cov=src/dash_ai --cov-report=html

# Run with verbose output
pytest tests/ -v

# Run with detailed output (including print statements)
pytest tests/ -vv -s
```

## Test Structure

### Directory Layout

```
tests/
├── conftest.py                    # Pytest fixtures
├── test_interfaces.py             # Core interfaces tests
├── test_config.py                 # Configuration tests
├── test_ingestion.py              # Markdown ingestion tests
├── test_storage.py                # Database storage tests
├── test_ollama.py                 # LLM integration tests
├── test_retrieval.py              # Document retrieval tests
├── test_answering.py              # RAG engine tests
├── test_cli.py                    # CLI interface tests
├── test_app.py                    # Application layer tests
└── fixtures/
    └── sample.md                  # Test fixture document
```

### Test Files Overview

| File | Tests | Purpose |
|------|-------|---------|
| `test_interfaces.py` | 5 | Validate Document and abstract classes |
| `test_config.py` | 6 | YAML loading, validation, env overrides |
| `test_ingestion.py` | 8 | Markdown parsing and chunking |
| `test_storage.py` | 14 | CRUD, search, persistence |
| `test_ollama.py` | 10 | LLM connection, retry logic, errors |
| `test_retrieval.py` | 6 | Document retrieval and scoring |
| `test_answering.py` | 7 | RAG pipeline, prompt building |
| `test_cli.py` | 11 | Command parsing and execution |
| `test_app.py` | 13 | Orchestration and workflows |

**Total: 79 tests, 100% pass rate, 90% coverage**

## Fixtures

Common test fixtures defined in `conftest.py`:

### `temp_db`
Temporary SQLite database for testing storage:
```python
def test_my_storage(temp_db):
    storage = SQLiteStorage(temp_db)
    # Test without affecting production database
```

### `sample_document`
Single test document:
```python
def test_retrieval(sample_document):
    # sample_document is a Document object
    assert sample_document.title == "Example"
```

### `sample_documents`
Multiple test documents for batch testing:
```python
def test_batch_operations(sample_documents):
    # sample_documents is a list of Document objects
    assert len(sample_documents) == 3
```

### `mock_ollama`
Mocked Ollama responses (no real LLM calls):
```python
def test_answer_generation(mock_ollama):
    model = OllamaModel(mock_ollama)
    response = model.generate("test prompt")
    assert response == "mocked response"
```

### `sample_config`
Test configuration (YAML + temp paths):
```python
def test_config_loading(sample_config):
    assert sample_config.model.host == "localhost"
    assert sample_config.storage.path.endswith(".db")
```

## Writing Tests

### Naming Convention

- Test files: `test_*.py`
- Test functions: `test_<component>_<behavior>`
- Test classes: `Test<Component>`

### Example Test

```python
def test_save_and_retrieve_document(temp_db):
    """Test that a saved document can be retrieved."""
    # Setup
    storage = SQLiteStorage(temp_db)
    doc = Document(
        id="doc1",
        title="Test",
        content="Hello world",
        source="test.md"
    )
    
    # Execute
    storage.save_document(doc)
    retrieved = storage.get_document("doc1")
    
    # Assert
    assert retrieved.title == "Test"
    assert retrieved.content == "Hello world"
```

### Test Structure (Arrange-Act-Assert)

```python
def test_something(fixture):
    # Arrange: Set up test data
    input_data = prepare_data()
    
    # Act: Execute code being tested
    result = function_under_test(input_data)
    
    # Assert: Verify expected outcome
    assert result == expected_value
```

### Mocking Dependencies

```python
from unittest.mock import Mock, patch

def test_with_mock():
    # Create mock
    mock_storage = Mock()
    mock_storage.save_document.return_value = None
    
    # Use mock
    retriever = Retriever(mock_storage)
    # retriever now uses mock instead of real storage
```

## Coverage

### Check Coverage

```bash
# Generate coverage report
pytest tests/ --cov=src/dash_ai --cov-report=html

# View report
open htmlcov/index.html  # macOS
# or browser to htmlcov/index.html
```

### Current Coverage

- Overall: **90%**
- Interfaces: **100%**
- Config: **100%**
- Ingestion: **95%**
- Storage: **92%**
- Ollama: **88%**
- Retrieval: **100%**
- Answering: **94%**
- CLI: **85%**
- App: **88%**

### Improving Coverage

1. Identify untested code: `pytest --cov-report=term-missing`
2. Write tests for missing lines
3. Focus on error paths and edge cases
4. Avoid testing framework/library code

## Common Test Patterns

### Testing Exceptions

```python
def test_missing_config_raises_error():
    """Test that missing config raises ValueError."""
    with pytest.raises(ValueError, match="Missing required config"):
        Config.load("nonexistent.yaml")
```

### Testing with Temporary Files

```python
def test_ingest_file(tmp_path):
    """Test ingesting a temporary markdown file."""
    md_file = tmp_path / "test.md"
    md_file.write_text("# Test\n\nContent")
    
    reader = MarkdownReader()
    docs = reader.read_file(str(md_file))
    
    assert len(docs) > 0
    assert docs[0].source == str(md_file)
```

### Testing Configuration Overrides

```python
def test_env_override_config(monkeypatch):
    """Test that environment variables override YAML."""
    monkeypatch.setenv("OLLAMA_MODEL", "custom-model")
    
    config = Config.load_with_env()
    
    assert config.model.model_name == "custom-model"
```

### Testing Database Operations

```python
def test_full_text_search(temp_db):
    """Test FTS5 search functionality."""
    storage = SQLiteStorage(temp_db)
    
    # Add documents
    storage.save_document(Document(..., content="Python programming"))
    storage.save_document(Document(..., content="JavaScript coding"))
    
    # Search
    results = storage.search("Python", top_k=5)
    
    # Verify
    assert len(results) == 1
    assert results[0][0].content.startswith("Python")
```

## Running Specific Test Subsets

```bash
# By keyword
pytest -k "storage" tests/          # Run tests matching "storage"
pytest -k "not ollama" tests/       # Run tests NOT matching "ollama"

# By marker
pytest -m "unit" tests/             # Run only unit tests
pytest -m "integration" tests/      # Run only integration tests

# By file pattern
pytest tests/test_storage.py        # Single file
pytest tests/test_*.py              # All test_*.py files

# First N tests
pytest --maxfail=1 tests/           # Stop after first failure
pytest -x tests/                    # Stop on first failure
pytest tests/ --tb=short            # Short traceback format
```

## Debug Tips

### Print Debugging

```python
def test_something():
    result = function()
    print(f"Result: {result}")  # See output with: pytest -vv -s
    assert result == expected
```

### Using pdb

```python
def test_debug():
    result = function()
    import pdb; pdb.set_trace()  # Breakpoint
    # Run: pytest tests/test_file.py -vv -s
```

### Check Test Dependencies

```bash
# List all fixtures
pytest --fixtures tests/

# Show setup/teardown order
pytest --setup-show tests/test_storage.py::test_name
```

## Best Practices

✅ **Do:**
- Test one thing per test function
- Use descriptive test names
- Use fixtures for common setup
- Test error cases and edge cases
- Keep tests fast (< 1 second each)
- Use mocks for external dependencies
- Document non-obvious tests

❌ **Don't:**
- Test framework features (they're already tested)
- Make tests dependent on each other
- Test implementation details (test behavior)
- Skip important edge cases
- Write slow tests (> 5 seconds)
- Mock everything (defeats integration testing)
- Leave debugging code in tests

## Continuous Integration

To run tests in CI/CD pipeline:

```yaml
# Example GitHub Actions
- name: Run tests
  run: pytest tests/ --cov=src/dash_ai --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

## Adding New Tests

When adding a new feature:

1. Write test first (TDD approach recommended)
2. Implement feature
3. Verify test passes
4. Check coverage: `pytest --cov`
5. Document test in this guide

Example workflow:

```bash
# 1. Create test file
cat > tests/test_new_feature.py << 'EOF'
def test_new_feature():
    result = new_feature()
    assert result == expected
EOF

# 2. Run test (fails initially)
pytest tests/test_new_feature.py

# 3. Implement feature
# ... (write code in src/)

# 4. Run test (passes)
pytest tests/test_new_feature.py

# 5. Check coverage
pytest tests/test_new_feature.py --cov
```

## Troubleshooting Tests

**"ModuleNotFoundError"**
- Ensure virtual environment activated: `source .venv/bin/activate`
- Reinstall dependencies: `uv sync`

**"Connection refused" in test**
- Tests should mock Ollama (see `test_ollama.py` for example)
- Check fixture isn't trying to connect to real Ollama

**"File not found" in test**
- Use fixtures like `tmp_path` instead of hardcoded paths
- Relative paths are relative to repository root

**"Flaky tests" (intermittent failures)**
- Check for hardcoded timings
- Don't rely on file system race conditions
- Mock time-based operations

**"Too many open files"**
- Tests may not be closing database connections
- Use context managers: `with sqlite3.connect() as conn:`
- Check fixtures clean up properly

## Performance

Current test suite:
- Total time: ~4 seconds
- Number of tests: 79
- Average per test: ~50ms
- Slowest test: ~500ms (storage batch operations)

To profile slow tests:
```bash
pytest tests/ --durations=10  # Show 10 slowest tests
```

## Further Reading

- [pytest documentation](https://docs.pytest.org/)
- [unittest.mock documentation](https://docs.python.org/3/library/unittest.mock.html)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)
