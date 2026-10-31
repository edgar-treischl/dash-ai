"""Test configuration and fixtures."""

import json
import sqlite3
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from dash_ai.core.interfaces import Document


@pytest.fixture
def temp_db(tmp_path):
    """Create a temporary SQLite database."""
    db_path = tmp_path / "test.db"
    return str(db_path)


@pytest.fixture
def sample_document():
    """Create a sample document for testing."""
    return Document(
        id="test_0",
        title="Test Document",
        content="This is test content about Python programming.",
        source="test.md",
        format="markdown",
        metadata={"chunk_index": 0, "total_chunks": 2},
    )


@pytest.fixture
def sample_documents():
    """Create multiple sample documents."""
    return [
        Document(
            id="doc1_0",
            title="Python Basics",
            content="Python is a high-level programming language known for simplicity.",
            source="python.md",
            format="markdown",
            metadata={"chunk_index": 0},
        ),
        Document(
            id="doc1_1",
            title="Python Basics",
            content="It supports multiple programming paradigms including OOP and functional.",
            source="python.md",
            format="markdown",
            metadata={"chunk_index": 1},
        ),
        Document(
            id="doc2_0",
            title="Web Development",
            content="FastAPI is a modern Python web framework for building APIs.",
            source="web.md",
            format="markdown",
            metadata={"chunk_index": 0},
        ),
    ]


@pytest.fixture
def mock_ollama():
    """Mock Ollama API responses."""
    with patch("requests.get") as mock_get, patch("requests.post") as mock_post:
        # Mock tags endpoint
        mock_get.return_value.json.return_value = {
            "models": [
                {"name": "mistral:latest"},
                {"name": "neural-chat:latest"},
            ]
        }

        # Mock generate endpoint
        mock_post.return_value.json.return_value = {
            "response": "This is a test response from Ollama."
        }

        yield mock_get, mock_post


@pytest.fixture
def sample_config(tmp_path):
    """Create a sample configuration file."""
    config_path = tmp_path / "settings.yaml"
    config_content = """
model:
  type: ollama
  name: mistral
  host: http://localhost:11434

storage:
  type: sqlite
  path: {}

retrieval:
  top_k: 5
  min_relevance: 0.0

app:
  data_dir: ./data/knowledge/
  debug: false
""".format(tmp_path / "test.db")

    with open(config_path, "w") as f:
        f.write(config_content)

    return str(config_path)
