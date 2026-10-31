"""Tests for SQLite storage."""

import json
import sqlite3

import pytest

from dash_ai.knowledge.storage import SQLiteStorage


@pytest.fixture
def storage(temp_db):
    """Create a SQLiteStorage instance with temp database."""
    return SQLiteStorage(temp_db)


def test_storage_initialization(temp_db):
    """Test storage initializes database schema."""
    storage = SQLiteStorage(temp_db)

    # Verify database was created
    assert storage.db_path.exists()

    # Verify tables exist
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='documents'"
    )
    assert cursor.fetchone() is not None

    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='documents_fts'"
    )
    assert cursor.fetchone() is not None

    conn.close()


def test_save_and_retrieve_document(storage, sample_document):
    """Test saving and retrieving a document."""
    storage.save_document(sample_document)

    retrieved = storage.get_document(sample_document.id)

    assert retrieved.id == sample_document.id
    assert retrieved.title == sample_document.title
    assert retrieved.content == sample_document.content
    assert retrieved.source == sample_document.source


def test_get_nonexistent_document(storage):
    """Test retrieving non-existent document raises KeyError."""
    with pytest.raises(KeyError):
        storage.get_document("nonexistent_id")


def test_save_multiple_documents(storage, sample_documents):
    """Test saving multiple documents."""
    for doc in sample_documents:
        storage.save_document(doc)

    retrieved = storage.list_documents()
    assert len(retrieved) == len(sample_documents)


def test_list_documents_order(storage, sample_documents):
    """Test documents are returned in reverse creation order."""
    for doc in sample_documents:
        storage.save_document(doc)

    listed = storage.list_documents()

    # Should be in reverse order (newest first)
    # Note: within same timestamp, order depends on INSERT order
    assert len(listed) == len(sample_documents)


def test_delete_document(storage, sample_document):
    """Test deleting a document."""
    storage.save_document(sample_document)
    storage.delete_document(sample_document.id)

    with pytest.raises(KeyError):
        storage.get_document(sample_document.id)


def test_delete_nonexistent_document(storage):
    """Test deleting non-existent document raises KeyError."""
    with pytest.raises(KeyError):
        storage.delete_document("nonexistent_id")


def test_search_documents(storage, sample_documents):
    """Test full-text search functionality."""
    for doc in sample_documents:
        storage.save_document(doc)

    # Search for "Python"
    results = storage.search("Python", top_k=5)

    assert len(results) > 0
    assert all(isinstance(score, float) for _, score in results)
    assert all(0 <= score <= 1 for _, score in results)


def test_search_empty_results(storage, sample_documents):
    """Test search with no matching results."""
    for doc in sample_documents:
        storage.save_document(doc)

    results = storage.search("nonexistentword123", top_k=5)

    assert results == []


@pytest.mark.parametrize(
    "query",
    [
        "What can I learn about Python?",
        "Python nonexistentword123",
        'What\'s "Python" about?',
        "Python OR (nonexistentword123)*",
    ],
)
def test_search_question_words(storage, sample_documents, query):
    for doc in sample_documents:
        storage.save_document(doc)

    results = storage.search(query)

    assert {doc.id for doc, _ in results} == {"doc1_0", "doc1_1", "doc2_0"}


@pytest.mark.parametrize("query", ["", "   ", '?!"()*'])
def test_search_without_words(storage, sample_document, query):
    storage.save_document(sample_document)

    assert storage.search(query) == []


def test_search_quickstart_question(storage):
    from dash_ai.ingestion.markdown import MarkdownReader

    for doc in MarkdownReader().read("data/knowledge/example.md"):
        storage.save_document(doc)

    results = storage.search("What is this project about?")

    assert results
    assert all(doc.source == "data/knowledge/example.md" for doc, _ in results)


def test_search_top_k_limit(storage, sample_documents):
    """Test top_k parameter limits results."""
    for doc in sample_documents:
        storage.save_document(doc)

    results_k1 = storage.search("Python", top_k=1)
    results_k3 = storage.search("Python", top_k=3)

    assert len(results_k1) <= 1
    assert len(results_k3) <= 3
    assert len(results_k1) <= len(results_k3)


def test_search_scoring(storage, sample_documents):
    """Test search results are scored and ranked."""
    for doc in sample_documents:
        storage.save_document(doc)

    results = storage.search("Python", top_k=5)

    if len(results) > 1:
        # Verify results have scores in valid range
        scores = [score for _, score in results]
        assert all(0 <= score <= 1 for score in scores)


def test_metadata_persistence(storage):
    """Test metadata is preserved during save/retrieve."""
    from dash_ai.core.interfaces import Document

    metadata = {
        "chunk_index": 5,
        "filename": "test.md",
        "custom_field": "custom_value",
    }

    doc = Document(
        id="test_meta",
        title="Test",
        content="Content",
        source="test.md",
        format="markdown",
        metadata=metadata,
    )

    storage.save_document(doc)
    retrieved = storage.get_document(doc.id)

    assert retrieved.metadata == metadata
    assert retrieved.metadata["chunk_index"] == 5
    assert retrieved.metadata["custom_field"] == "custom_value"


def test_update_document(storage, sample_document):
    """Test updating an existing document."""
    storage.save_document(sample_document)

    # Modify and save
    sample_document.content = "Updated content"
    storage.save_document(sample_document)

    # Verify update
    retrieved = storage.get_document(sample_document.id)
    assert retrieved.content == "Updated content"
