"""Tests for Ollama model integration."""

import pytest
import requests
from unittest.mock import Mock, patch

from dash_ai.core.errors import ModelError
from dash_ai.models.ollama import OllamaModel


@pytest.fixture
def mock_ollama_server():
    """Mock Ollama server."""
    with patch("requests.get") as mock_get, patch("requests.post") as mock_post:
        # Mock tags response
        mock_get.return_value.json.return_value = {
            "models": [{"name": "mistral:latest"}]
        }
        mock_get.return_value.raise_for_status = Mock()

        # Mock generate response
        mock_post.return_value.json.return_value = {
            "response": "This is the generated response."
        }
        mock_post.return_value.raise_for_status = Mock()

        yield mock_get, mock_post


def test_ollama_initialization(mock_ollama_server):
    """Test Ollama model initialization."""
    model = OllamaModel("http://localhost:11434", "mistral")

    assert model.host == "http://localhost:11434"
    assert model.model == "mistral"


def test_ollama_host_normalization(mock_ollama_server):
    """Test that trailing slash is removed from host."""
    model = OllamaModel("http://localhost:11434/", "mistral")

    assert model.host == "http://localhost:11434"


def test_ollama_connection_error():
    """Test error when Ollama is not accessible."""
    with patch("requests.get") as mock_get:
        mock_get.side_effect = requests.exceptions.ConnectionError()

        with pytest.raises(ModelError, match="Cannot connect to Ollama"):
            OllamaModel("http://localhost:11434", "mistral")


def test_ollama_model_not_found():
    """Test error when requested model is not available."""
    with patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = {"models": [{"name": "other:latest"}]}
        mock_get.return_value.raise_for_status = Mock()

        with pytest.raises(ModelError, match="Model 'mistral' not found"):
            OllamaModel("http://localhost:11434", "mistral")


def test_ollama_generate(mock_ollama_server):
    """Test generating response from model."""
    model = OllamaModel("http://localhost:11434", "mistral")
    response = model.generate("What is Python?")

    assert response == "This is the generated response."


def test_ollama_generate_strips_whitespace(mock_ollama_server):
    """Test that generated response is stripped of whitespace."""
    _, mock_post = mock_ollama_server
    mock_post.return_value.json.return_value = {
        "response": "  Response with whitespace  \n"
    }
    mock_post.return_value.raise_for_status = Mock()

    model = OllamaModel("http://localhost:11434", "mistral")
    response = model.generate("Test")

    assert response == "Response with whitespace"


def test_ollama_get_model_name(mock_ollama_server):
    """Test getting model name."""
    model = OllamaModel("http://localhost:11434", "mistral")

    assert model.get_model_name() == "mistral"


def test_ollama_retry_on_timeout():
    """Test retry logic on timeout."""
    with patch("requests.post") as mock_post, patch("requests.get") as mock_get:
        # Mock initialization
        mock_get.return_value.json.return_value = {"models": [{"name": "mistral:latest"}]}
        mock_get.return_value.raise_for_status = Mock()

        # Mock generate failures then success
        mock_post.side_effect = [
            requests.exceptions.Timeout(),
            requests.exceptions.Timeout(),
            Mock(json=lambda: {"response": "Success"}),
        ]

        model = OllamaModel("http://localhost:11434", "mistral")
        response = model.generate("Test")

        assert response == "Success"
        assert mock_post.call_count == 3


def test_ollama_max_retries_exceeded():
    """Test error after max retries exceeded."""
    with patch("requests.post") as mock_post, patch("requests.get") as mock_get:
        # Mock initialization
        mock_get.return_value.json.return_value = {"models": [{"name": "mistral:latest"}]}
        mock_get.return_value.raise_for_status = Mock()

        # All attempts fail
        mock_post.side_effect = requests.exceptions.ConnectionError("Always fails")

        model = OllamaModel("http://localhost:11434", "mistral", max_retries=2)

        with pytest.raises(ModelError, match="Failed to generate response"):
            model.generate("Test")

        assert mock_post.call_count == 2


def test_ollama_invalid_response():
    """Test error handling for invalid API response."""
    with patch("requests.post") as mock_post, patch("requests.get") as mock_get:
        # Mock initialization
        mock_get.return_value.json.return_value = {"models": [{"name": "mistral:latest"}]}
        mock_get.return_value.raise_for_status = Mock()

        # Mock invalid response
        mock_post.return_value.json.return_value = {"invalid": "response"}
        mock_post.return_value.raise_for_status = Mock()

        model = OllamaModel("http://localhost:11434", "mistral", max_retries=1)

        with pytest.raises(ModelError, match="Failed to generate response"):
            model.generate("Test")
