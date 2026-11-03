# Test Suite Guide for dash-ai

## Quick Start

### Run All Tests
```bash
cd /Users/edgar/Development/dash/dash-ai
make test  # or: uv run --extra dev pytest tests/
```

Expected output:
- **221 tests pass** in ~5 seconds
- **92% code coverage** maintained

### Run Specific Test Files
```bash
# Run only edge case tests
uv run --extra dev pytest tests/test_edge_cases.py -v

# Run only performance tests
uv run --extra dev pytest tests/test_performance_benchmarks.py -v

# Run only storage tests
uv run --extra dev pytest tests/test_storage.py -v
```

### Run Tests with Coverage Report
```bash
uv run --extra dev pytest tests/ --cov=src/dash_ai --cov-report=html
# Open htmlcov/index.html to view detailed coverage
```

## Test Organization

### By Component

**Core Components**
- `test_config.py` - Configuration loading and validation
- `test_errors.py` - Custom exception hierarchy
- `test_interfaces.py` - Abstract interfaces and contracts

**Ingestion**
- `test_ingestion.py` - Markdown file reading and processing
- `test_edge_cases.py::TestIngestionErrorCases` - Ingestion edge cases

**Storage**
- `test_storage.py` - SQLite document storage
- `test_edge_cases.py::TestEmptyDatabaseEdgeCases` - Empty database handling
- `test_edge_cases.py::TestDatabaseRecovery` - Recovery scenarios

**Retrieval & Answering**
- `test_retrieval.py` - Document retrieval
- `test_answering.py` - Answer generation engine

**CLI & Interfaces**
- `test_cli.py` - Command-line interface
- `test_cli_json.py` - JSON output formatting
- `test_cli_progress.py` - Progress indicators
- `test_interactive.py` - Interactive mode

**Model Integration**
- `test_ollama.py` - Ollama LLM interface

**Utilities**
- `test_json_formatter.py` - JSON formatting
- `test_progress.py` - Progress tracking components

**Robustness**
- `test_edge_cases.py` - 30 edge case tests
- `test_performance_benchmarks.py` - 17 performance tests

### By Category

**Unit Tests** (~120 tests)
- Isolated component behavior
- Single responsibility testing
- Fast execution (< 50ms each)

**Integration Tests** (~60 tests)
- Component interaction
- End-to-end workflows
- Database + Model + Retrieval chains

**Performance Tests** (~17 tests)
- Regression detection
- Throughput benchmarks
- Latency measurements

**Edge Case Tests** (~30 tests)
- Empty databases
- Large files
- Unicode handling
- Special characters
- Malformed input
- Concurrent access

**Error Handling** (~40+ tests)
- Exception scenarios
- Recovery paths
- Error message quality

## Key Test Scenarios

### Ingestion Tests
- ✓ Read Markdown files and extract content
- ✓ Chunk large documents
- ✓ Handle encoding issues (UTF-8)
- ✓ Extract titles and metadata
- ✓ Validate document IDs

### Storage Tests
- ✓ Save and retrieve documents
- ✓ Search with relevance scoring
- ✓ List all documents
- ✓ Delete documents
- ✓ Handle concurrent access
- ✓ Persist metadata

### Retrieval Tests
- ✓ Retrieve relevant documents
- ✓ Respect top_k parameter
- ✓ Return scoring tuples
- ✓ Handle empty results

### CLI Tests
- ✓ `ingest` command
- ✓ `ask` command
- ✓ `chat` command (interactive)
- ✓ `list` command
- ✓ `delete` command
- ✓ `--json` flag
- ✓ Error handling

### Model Tests
- ✓ Ollama connection
- ✓ Model generation
- ✓ Timeout handling
- ✓ Retry logic
- ✓ Response parsing

## Performance Baselines

### Ingestion
- Single file: **< 1.0 second**
- 50 documents: **< 2.0 seconds**

### Search
- Small DB (10 docs): **< 100ms**
- Medium DB (100 docs): **< 200ms**
- Large DB (500 docs): **< 200ms**

### Retrieval
- Single document: **< 10ms**
- 100 sequential gets: **< 1.0 second**

### Database Operations
- List 100 documents: **< 200ms**
- Delete 25 documents: **< 1.0 second**
- Update 50 documents: **< 1.0 second**

## Running Specific Tests

### Run a single test
```bash
uv run --extra dev pytest tests/test_storage.py::test_save_and_retrieve_document -v
```

### Run tests matching a pattern
```bash
# All storage tests
uv run --extra dev pytest tests/ -k storage -v

# All search tests
uv run --extra dev pytest tests/ -k search -v

# All performance tests
uv run --extra dev pytest tests/ -k performance -v
```

### Run with detailed output
```bash
# Show print statements and full tracebacks
uv run --extra dev pytest tests/test_storage.py -v -s

# Show variables on failure
uv run --extra dev pytest tests/ -v --tb=long
```

### Run slow tests only
```bash
uv run --extra dev pytest tests/ -m slow -v
```

## Debugging Failed Tests

### Get full error details
```bash
uv run --extra dev pytest tests/test_file.py::test_name -v --tb=long
```

### Run with print statements visible
```bash
uv run --extra dev pytest tests/test_file.py::test_name -v -s
```

### Drop into debugger on failure
```bash
uv run --extra dev pytest tests/test_file.py::test_name -v --pdb
```

## Test Fixtures

Common fixtures available in conftest.py:

- `temp_db` - Temporary SQLite database
- `sample_document` - Single test Document
- `sample_documents` - Multiple test Documents
- `mock_ollama` - Mocked Ollama responses
- `sample_config` - Test configuration file

Example usage:
```python
def test_storage(temp_db, sample_document):
    storage = SQLiteStorage(temp_db)
    storage.save_document(sample_document)
    assert storage.get_document(sample_document.id) is not None
```

## Adding New Tests

### Location
- Add to existing file if testing an existing module
- Create new file: `tests/test_new_feature.py`

### Template
```python
import pytest
from dash_ai.core.interfaces import Document
from dash_ai.knowledge.storage import SQLiteStorage

class TestNewFeature:
    """Test description."""
    
    def test_basic_behavior(self, temp_db, sample_document):
        """Test what this does."""
        storage = SQLiteStorage(temp_db)
        # Arrange
        storage.save_document(sample_document)
        
        # Act
        result = storage.get_document(sample_document.id)
        
        # Assert
        assert result is not None
        assert result.id == sample_document.id
```

### Guidelines
- One behavior per test
- Clear, descriptive test names
- Use fixtures for setup
- Mock external dependencies
- Include docstrings
- Test both success and failure cases

## Coverage Report

### View HTML coverage report
```bash
uv run --extra dev pytest tests/ --cov=src/dash_ai --cov-report=html
open htmlcov/index.html
```

### View terminal coverage report
```bash
uv run --extra dev pytest tests/ --cov=src/dash_ai --cov-report=term-missing
```

### Target coverage by module
- Core: 100%
- Answering: 100%
- Interactive: 100%
- Progress: 100%
- JSON Formatter: 100%
- Errors: 100%
- Ingestion: 94%
- Storage: 90%
- Ollama: 96%
- App: 99%
- CLI: 89%
- Interfaces: 78% (abstract methods)
- Config: 68% (env override paths)

## Continuous Integration

When modifying code:

1. **Run affected tests**
   ```bash
   uv run --extra dev pytest tests/test_modified_module.py -v
   ```

2. **Run full suite**
   ```bash
   uv run --extra dev pytest tests/ -v
   ```

3. **Check coverage doesn't drop**
   ```bash
   uv run --extra dev pytest tests/ --cov=src/dash_ai
   ```

4. **Commit with confidence**
   ```bash
   git add .
   git commit -m "Feature: description"
   ```

## Performance Regression Detection

Performance tests check for regressions in:
- Ingestion speed
- Search latency
- Memory efficiency
- Database operation speed

If tests fail:
1. Check if actual performance degraded
2. Profile with `cProfile`
3. Consider adding database indexes
4. Review query optimization

## Common Issues

### Tests timeout
- Increase wait time in async operations
- Check if Ollama is running (for integration tests)
- Run single test to isolate issue

### Flaky tests
- Check for time-dependent assertions
- Verify proper fixture isolation
- Review mock setups

### Coverage drops
- Add tests for uncovered lines
- Check for new conditional branches
- Ensure error paths tested

## Troubleshooting

### "Module not found"
```bash
# Reinstall package in editable mode
uv pip install -e .
```

### "ImportError: No module named 'dash_ai'"
```bash
# Set PYTHONPATH
export PYTHONPATH=src
uv run pytest tests/
```

### Tests pass locally but fail in CI
- Check Python version compatibility
- Verify all dependencies installed
- Check for platform-specific issues (Windows paths, etc.)

## Resources

- Pytest docs: https://docs.pytest.org/
- Coverage.py docs: https://coverage.readthedocs.io/
- Python testing best practices: https://docs.python-guide.org/writing/tests/
