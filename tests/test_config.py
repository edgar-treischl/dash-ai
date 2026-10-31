"""Tests for configuration management."""

import os
from pathlib import Path

import pytest

from dash_ai.core.config import Config


def test_config_loads_yaml(sample_config):
    """Test that config loads from YAML file."""
    config = Config(sample_config)

    assert config.get("model", "type") == "ollama"
    assert config.get("model", "name") == "mistral"
    assert config.get("storage", "type") == "sqlite"


def test_config_missing_file():
    """Test error when config file not found."""
    with pytest.raises(FileNotFoundError):
        Config("nonexistent.yaml")


def test_config_validation_missing_section(tmp_path):
    """Test validation catches missing sections or fields."""
    config_file = tmp_path / "settings.yaml"
    with open(config_file, "w") as f:
        f.write("model:\n  type: ollama\n")

    with pytest.raises(ValueError, match="Missing required config"):
        Config(str(config_file))


def test_config_env_override(sample_config, monkeypatch):
    """Test environment variable overrides."""
    monkeypatch.setenv("OLLAMA_HOST", "http://custom:11434")

    config = Config(sample_config)
    assert config.get("model", "host") == "http://custom:11434"


def test_config_get_section(sample_config):
    """Test getting entire config section."""
    config = Config(sample_config)

    model_section = config.get_section("model")
    assert "type" in model_section
    assert "name" in model_section
    assert "host" in model_section


def test_config_get_default(sample_config):
    """Test default value for missing keys."""
    config = Config(sample_config)

    value = config.get("nonexistent", "key", default="default_value")
    assert value == "default_value"
