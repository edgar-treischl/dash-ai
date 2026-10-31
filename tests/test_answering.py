"""Tests for answering engine."""

import pytest
from unittest.mock import Mock

from dash_ai.answering.engine import AnsweringEngine


def test_answering_engine_initialization():
    """Test AnsweringEngine initialization."""
    mock_retriever = Mock()
    mock_model = Mock()

    engine = AnsweringEngine(mock_retriever, mock_model)

    assert engine.retriever == mock_retriever
    assert engine.model == mock_model


def test_answering_engine_answer(sample_documents):
    """Test answering a question."""
    mock_retriever = Mock()
    mock_retriever.retrieve.return_value = [
        (sample_documents[0], 0.95),
        (sample_documents[1], 0.87),
    ]

    mock_model = Mock()
    mock_model.generate.return_value = "Python is a versatile programming language."

    engine = AnsweringEngine(mock_retriever, mock_model)
    answer, sources = engine.answer("What is Python?", top_k=5)

    assert "Answer:" in answer
    assert "Sources:" in answer
    assert len(sources) == 2

    # Verify retriever was called
    mock_retriever.retrieve.assert_called_once_with("What is Python?", top_k=5)

    # Verify model was called with prompt
    mock_model.generate.assert_called_once()
    prompt = mock_model.generate.call_args[0][0]
    assert "Based on the following information:" in prompt
    assert "What is Python?" in prompt


def test_answering_engine_no_documents():
    """Test answering when no documents found."""
    mock_retriever = Mock()
    mock_retriever.retrieve.return_value = []

    mock_model = Mock()

    engine = AnsweringEngine(mock_retriever, mock_model)
    answer, sources = engine.answer("Obscure question")

    assert "couldn't find" in answer
    assert sources == []
    # Model should not be called if no documents
    mock_model.generate.assert_not_called()


def test_answering_engine_source_formatting(sample_documents):
    """Test source references are properly formatted."""
    mock_retriever = Mock()
    mock_retriever.retrieve.return_value = [
        (sample_documents[0], 0.95),
    ]

    mock_model = Mock()
    mock_model.generate.return_value = "Test answer"

    engine = AnsweringEngine(mock_retriever, mock_model)
    answer, sources = engine.answer("Test")

    assert sources[0].source in answer
    assert "chunk" in answer
    assert "Sources:" in answer


def test_answering_engine_context_building(sample_documents):
    """Test that context is built from retrieved documents."""
    mock_retriever = Mock()
    mock_retriever.retrieve.return_value = [
        (sample_documents[0], 0.95),
        (sample_documents[1], 0.87),
    ]

    mock_model = Mock()
    mock_model.generate.return_value = "Answer"

    engine = AnsweringEngine(mock_retriever, mock_model)
    engine.answer("Question")

    # Verify model received prompt with document content
    prompt = mock_model.generate.call_args[0][0]
    assert sample_documents[0].content in prompt
    assert sample_documents[1].content in prompt


def test_answering_engine_top_k_parameter(sample_documents):
    """Test top_k parameter is passed to retriever."""
    mock_retriever = Mock()
    mock_retriever.retrieve.return_value = []

    mock_model = Mock()

    engine = AnsweringEngine(mock_retriever, mock_model)
    engine.answer("Question", top_k=10)

    mock_retriever.retrieve.assert_called_once_with("Question", top_k=10)


def test_answering_engine_prompt_structure(sample_documents):
    """Test prompt structure matches expected format."""
    mock_retriever = Mock()
    mock_retriever.retrieve.return_value = [
        (sample_documents[0], 0.95),
    ]

    mock_model = Mock()
    mock_model.generate.return_value = "Generated answer"

    engine = AnsweringEngine(mock_retriever, mock_model)
    engine.answer("Test question")

    prompt = mock_model.generate.call_args[0][0]

    # Verify prompt structure
    assert "Based on the following information:" in prompt
    assert "Answer this question in German:" in prompt
    assert sample_documents[0].content in prompt
    assert "Test question" in prompt
