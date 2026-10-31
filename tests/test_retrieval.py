"""Tests for retrieval engine."""

import pytest
from unittest.mock import Mock

from dash_ai.answering.retrieval import Retriever
from dash_ai.core.interfaces import Document


def test_retriever_initialization():
    """Test Retriever initialization."""
    mock_storage = Mock()
    retriever = Retriever(mock_storage)

    assert retriever.storage == mock_storage


def test_retriever_retrieve(sample_documents):
    """Test document retrieval."""
    mock_storage = Mock()
    mock_storage.search.return_value = [
        (sample_documents[0], 0.95),
        (sample_documents[1], 0.87),
    ]

    retriever = Retriever(mock_storage)
    results = retriever.retrieve("Python", top_k=5)

    assert len(results) == 2
    assert all(isinstance(doc, Document) for doc, _ in results)
    assert all(isinstance(score, float) for _, score in results)

    # Verify storage was called correctly
    mock_storage.search.assert_called_once_with("Python", top_k=5)


def test_retriever_empty_results():
    """Test retriever with no results."""
    mock_storage = Mock()
    mock_storage.search.return_value = []

    retriever = Retriever(mock_storage)
    results = retriever.retrieve("nonexistent", top_k=5)

    assert results == []


def test_retriever_top_k_parameter(sample_documents):
    """Test top_k parameter is passed to storage."""
    mock_storage = Mock()
    mock_storage.search.return_value = []

    retriever = Retriever(mock_storage)
    retriever.retrieve("test", top_k=10)

    mock_storage.search.assert_called_once_with("test", top_k=10)


def test_retriever_default_top_k(sample_documents):
    """Test default top_k parameter."""
    mock_storage = Mock()
    mock_storage.search.return_value = []

    retriever = Retriever(mock_storage)
    retriever.retrieve("test")

    # Default top_k should be 5
    mock_storage.search.assert_called_once_with("test", top_k=5)


def test_retriever_preserves_scores(sample_documents):
    """Test that retriever preserves relevance scores from storage."""
    mock_storage = Mock()
    test_score = 0.73
    mock_storage.search.return_value = [
        (sample_documents[0], test_score),
    ]

    retriever = Retriever(mock_storage)
    results = retriever.retrieve("Python")

    assert results[0][1] == test_score
