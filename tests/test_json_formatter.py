"""Tests for JSON output formatting."""

import json
import pytest
from unittest.mock import Mock

from dash_ai.json_formatter import JSONFormatter
from dash_ai.core.interfaces import Document


def test_json_formatter_ingest_success():
    """Test JSON formatting for successful ingestion."""
    output = JSONFormatter.ingest_success(num_files=3, num_chunks=42)
    data = json.loads(output)

    assert data["status"] == "success"
    assert data["files_imported"] == 3
    assert data["chunks_created"] == 42


def test_json_formatter_ask_success():
    """Test JSON formatting for successful question answer."""
    doc1 = Mock(spec=Document)
    doc1.id = "doc-1"
    doc1.source = "file1.md"
    doc1.content = "This is a test document about Python programming."

    doc2 = Mock(spec=Document)
    doc2.id = "doc-2"
    doc2.source = "file2.md"
    doc2.content = "Another document with some content."

    sources = [(doc1, 0.95), (doc2, 0.73)]

    output = JSONFormatter.ask_success(
        question="What is Python?",
        answer="Python is a programming language.",
        sources=sources,
        generation_time_ms=1234.56,
    )
    data = json.loads(output)

    assert data["status"] == "success"
    assert data["question"] == "What is Python?"
    assert data["answer"] == "Python is a programming language."
    assert data["generation_time_ms"] == 1234.56

    assert len(data["sources"]) == 2
    assert data["sources"][0]["document_id"] == "doc-1"
    assert data["sources"][0]["relevance_score"] == 0.95
    assert data["sources"][1]["document_id"] == "doc-2"
    assert data["sources"][1]["relevance_score"] == 0.73


def test_json_formatter_ask_success_truncates_long_excerpts():
    """Test that long excerpts are truncated in JSON output."""
    doc = Mock(spec=Document)
    doc.id = "doc-1"
    doc.source = "file.md"
    doc.content = "x" * 500  # Very long content

    sources = [(doc, 0.9)]

    output = JSONFormatter.ask_success(
        question="Test?",
        answer="Answer.",
        sources=sources,
        generation_time_ms=100.0,
    )
    data = json.loads(output)

    excerpt = data["sources"][0]["excerpt"]
    assert len(excerpt) <= 203  # 200 chars + "..."
    assert excerpt.endswith("...")


def test_json_formatter_list_success_empty():
    """Test JSON formatting for empty document list."""
    output = JSONFormatter.list_success([])
    data = json.loads(output)

    assert data["status"] == "success"
    assert data["documents"] == []
    assert data["total_documents"] == 0
    assert data["total_chunks"] == 0


def test_json_formatter_list_success_with_docs():
    """Test JSON formatting for document list."""
    documents = [
        ("file1.md", 10, 5.2),
        ("file2.md", 20, 10.5),
        ("file3.md", 5, 2.1),
    ]

    output = JSONFormatter.list_success(documents)
    data = json.loads(output)

    assert data["status"] == "success"
    assert len(data["documents"]) == 3
    assert data["total_documents"] == 3
    assert data["total_chunks"] == 35

    assert data["documents"][0]["source"] == "file1.md"
    assert data["documents"][0]["chunks"] == 10
    assert data["documents"][0]["size_kb"] == 5.2


def test_json_formatter_delete_success():
    """Test JSON formatting for successful delete."""
    output = JSONFormatter.delete_success("doc-abc-123")
    data = json.loads(output)

    assert data["status"] == "success"
    assert data["deleted_document"] == "doc-abc-123"


def test_json_formatter_error_with_suggestion():
    """Test JSON error formatting with suggestion."""
    output = JSONFormatter.error(
        error_message="Configuration file not found",
        error_type="ConfigurationError",
        suggestion="Run 'dash-ai config init' to create default config",
    )
    data = json.loads(output)

    assert data["status"] == "error"
    assert data["error_type"] == "ConfigurationError"
    assert data["error_message"] == "Configuration file not found"
    assert data["suggestion"] == "Run 'dash-ai config init' to create default config"


def test_json_formatter_error_without_suggestion():
    """Test JSON error formatting without suggestion."""
    output = JSONFormatter.error(
        error_message="Unknown error occurred",
        error_type="Exception",
    )
    data = json.loads(output)

    assert data["status"] == "error"
    assert data["error_type"] == "Exception"
    assert data["error_message"] == "Unknown error occurred"
    assert "suggestion" not in data


def test_json_formatter_success_response():
    """Test generic success response."""
    output = JSONFormatter.success_response({"count": 42, "name": "test"})
    data = json.loads(output)

    assert data["status"] == "success"
    assert data["count"] == 42
    assert data["name"] == "test"


def test_json_formatter_error_response():
    """Test generic error response."""
    output = JSONFormatter.error_response(
        message="Something went wrong",
        error_type="RuntimeError",
        suggestion="Check the logs",
    )
    data = json.loads(output)

    assert data["status"] == "error"
    assert data["error_type"] == "RuntimeError"
    assert data["error_message"] == "Something went wrong"
    assert data["suggestion"] == "Check the logs"
