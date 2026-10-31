"""Tests for custom error handling."""

import pytest

from dash_ai.core.errors import (
    ConfigurationError,
    DashAIError,
    IngestionError,
    ModelError,
    RetrievalError,
    StorageError,
)


def test_dashaiexception_base():
    """Test base DashAI exception."""
    error = DashAIError("Test error")
    assert "Test error" in str(error)


def test_dashaiexception_with_suggestion():
    """Test exception with recovery suggestion."""
    error = DashAIError("Connection failed", suggestion="Check if service is running")
    assert "Connection failed" in str(error)
    assert "Check if service is running" in str(error)
    assert "💡 Tip:" in str(error)


def test_configuration_error():
    """Test ConfigurationError."""
    error = ConfigurationError("Missing config", suggestion="Create config file")
    assert isinstance(error, DashAIError)
    assert "Missing config" in str(error)


def test_storage_error():
    """Test StorageError."""
    error = StorageError("Database error", suggestion="Check permissions")
    assert isinstance(error, DashAIError)
    assert "Database error" in str(error)


def test_model_error():
    """Test ModelError."""
    error = ModelError("Model not found", suggestion="Run 'ollama pull model'")
    assert isinstance(error, DashAIError)
    assert "Model not found" in str(error)


def test_retrieval_error():
    """Test RetrievalError."""
    error = RetrievalError("Search failed", suggestion="Check database")
    assert isinstance(error, DashAIError)
    assert "Search failed" in str(error)


def test_ingestion_error():
    """Test IngestionError."""
    error = IngestionError("Failed to read file", suggestion="Check file format")
    assert isinstance(error, DashAIError)
    assert "Failed to read file" in str(error)


def test_error_suggestion_optional():
    """Test error without suggestion."""
    error = DashAIError("Error message")
    assert "Error message" in str(error)
    assert "💡 Tip:" not in str(error)


def test_error_is_exception():
    """Test that custom errors are proper exceptions."""
    error = DashAIError("Test")
    assert isinstance(error, Exception)
    assert isinstance(error, DashAIError)
