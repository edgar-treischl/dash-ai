"""Tests for application layer."""

import pytest
from unittest.mock import Mock, patch

from dash_ai.app import App
from dash_ai.core.errors import ConfigurationError, StorageError


def test_app_initialization(sample_config, mock_ollama):
    """Test App initialization with all components."""
    app = App(sample_config)

    assert app.config is not None
    assert app.storage is not None
    assert app.model is not None
    assert app.retriever is not None
    assert app.engine is not None


def test_app_config_loading(sample_config, mock_ollama):
    """Test configuration is loaded correctly."""
    app = App(sample_config)

    assert app.config.get("model", "type") == "ollama"
    assert app.config.get("storage", "type") == "sqlite"


def test_app_ingest_files(sample_config, tmp_path, mock_ollama):
    """Test ingesting files."""
    # Create test markdown file
    md_file = tmp_path / "test.md"
    md_file.write_text("# Title\n\nContent paragraph 1\n\nContent paragraph 2")

    app = App(sample_config)
    num_files, num_chunks = app.ingest_files(str(md_file))

    assert num_files == 1
    assert num_chunks > 0


def test_app_ingest_directory(sample_config, tmp_path, mock_ollama):
    """Test ingesting from directory."""
    # Create multiple markdown files
    md_file1 = tmp_path / "doc1.md"
    md_file1.write_text("# Doc 1\n\nContent")

    md_file2 = tmp_path / "doc2.md"
    md_file2.write_text("# Doc 2\n\nMore content")

    app = App(sample_config)
    num_files, num_chunks = app.ingest_files(str(tmp_path))

    assert num_files == 2
    assert num_chunks > 0


def test_app_ingest_file_not_found(sample_config, mock_ollama):
    """Test error when file not found."""
    app = App(sample_config)

    with pytest.raises(FileNotFoundError):
        app.ingest_files("nonexistent.md")


def test_app_ingest_no_markdown_files(sample_config, tmp_path, mock_ollama):
    """Test error when directory has no Markdown files."""
    app = App(sample_config)

    with pytest.raises(ValueError):
        app.ingest_files(str(tmp_path))


def test_app_ask_question(sample_config, mock_ollama, tmp_path):
    """Test asking a question."""
    # Create and ingest a document first
    md_file = tmp_path / "test.md"
    md_file.write_text("# Title\n\nPython is great")

    app = App(sample_config)
    app.ingest_files(str(md_file))

    answer = app.ask_question("Python", top_k=1)

    assert "Answer:" in answer


def test_app_list_documents(sample_config, tmp_path, mock_ollama):
    """Test listing documents."""
    md_file = tmp_path / "test.md"
    md_file.write_text("# Title\n\nContent")

    app = App(sample_config)
    app.ingest_files(str(md_file))

    documents = app.list_documents()

    assert len(documents) > 0
    assert all(isinstance(source, str) for source, _, _ in documents)
    assert all(isinstance(chunks, int) for _, chunks, _ in documents)
    assert all(isinstance(size, float) for _, _, size in documents)


def test_app_list_documents_empty(sample_config, mock_ollama):
    """Test listing documents when empty."""
    app = App(sample_config)

    documents = app.list_documents()

    assert documents == []


def test_app_delete_document(sample_config, tmp_path, mock_ollama):
    """Test deleting a document."""
    md_file = tmp_path / "test.md"
    md_file.write_text("# Title\n\nContent")

    app = App(sample_config)
    app.ingest_files(str(md_file))

    # Get first document ID
    documents = app.storage.list_documents()
    doc_id = documents[0].id

    # Delete it
    app.delete_document(doc_id)

    # Verify it's gone
    with pytest.raises(StorageError):
        app.get_document(doc_id)


def test_app_get_document(sample_config, tmp_path, mock_ollama):
    """Test retrieving a specific document."""
    md_file = tmp_path / "test.md"
    md_file.write_text("# Title\n\nContent")

    app = App(sample_config)
    app.ingest_files(str(md_file))

    # Get first document
    documents = app.storage.list_documents()
    retrieved = app.get_document(documents[0].id)

    assert retrieved.id == documents[0].id
    assert retrieved.title == documents[0].title


def test_app_missing_config():
    """Test error when config file is missing."""
    with pytest.raises(ConfigurationError):
        App("nonexistent.yaml")


def test_app_invalid_config(tmp_path):
    """Test error when config is invalid."""
    config_file = tmp_path / "settings.yaml"
    config_file.write_text("invalid: config")

    with pytest.raises(ConfigurationError):
        App(str(config_file))
