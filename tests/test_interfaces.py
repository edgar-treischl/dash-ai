"""Tests for core interfaces."""

import pytest

from dash_ai.core.interfaces import Document, ModelInterface, ReaderInterface, StorageInterface


def test_document_creation():
    """Test Document dataclass creation."""
    doc = Document(
        id="test_1",
        title="Test",
        content="Test content",
        source="test.md",
        format="markdown",
    )

    assert doc.id == "test_1"
    assert doc.title == "Test"
    assert doc.content == "Test content"
    assert doc.source == "test.md"
    assert doc.format == "markdown"
    assert doc.metadata == {}


def test_document_with_metadata():
    """Test Document with metadata."""
    metadata = {"chunk_index": 0, "filename": "test.md"}
    doc = Document(
        id="test_1",
        title="Test",
        content="Content",
        source="test.md",
        format="markdown",
        metadata=metadata,
    )

    assert doc.metadata == metadata
    assert doc.metadata["chunk_index"] == 0


def test_model_interface_abstract():
    """Test that ModelInterface cannot be instantiated directly."""
    with pytest.raises(TypeError):
        ModelInterface()


def test_reader_interface_abstract():
    """Test that ReaderInterface cannot be instantiated directly."""
    with pytest.raises(TypeError):
        ReaderInterface()


def test_storage_interface_abstract():
    """Test that StorageInterface cannot be instantiated directly."""
    with pytest.raises(TypeError):
        StorageInterface()
