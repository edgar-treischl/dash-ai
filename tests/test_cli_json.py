"""Tests for CLI JSON output integration."""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock

from dash_ai.cli import cmd_ingest, cmd_ask, cmd_list, cmd_delete
from dash_ai.core.errors import ConfigurationError, StorageError


class TestCLIJsonOutput:
    """Tests for JSON output in CLI commands."""

    def test_cmd_ingest_json_output(self, capsys):
        """Test ingest command with --json flag."""
        app = Mock()
        app.ingest_files.return_value = (3, 42)

        args = Mock()
        args.path = "data/"
        args.json = True

        result = cmd_ingest(app, args)

        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)

        assert data["status"] == "success"
        assert data["files_imported"] == 3
        assert data["chunks_created"] == 42

    def test_cmd_ingest_text_output(self, capsys):
        """Test ingest command without --json flag."""
        app = Mock()
        app.ingest_files.return_value = (2, 20)

        args = Mock()
        args.path = "data/"
        args.json = False

        result = cmd_ingest(app, args)

        assert result == 0
        captured = capsys.readouterr()
        assert "✓ Imported 2 file(s) with 20 chunk(s)" in captured.out

    def test_cmd_ingest_json_error_output(self, capsys):
        """Test ingest command with --json flag on error."""
        app = Mock()
        app.ingest_files.side_effect = StorageError("Database error")

        args = Mock()
        args.path = "data/"
        args.json = True

        result = cmd_ingest(app, args)

        assert result == 1
        captured = capsys.readouterr()
        data = json.loads(captured.err)

        assert data["status"] == "error"
        assert data["error_type"] == "StorageError"
        assert "Database error" in data["error_message"]

    def test_cmd_ask_json_output(self, capsys):
        """Test ask command with --json flag."""
        mock_doc = Mock()
        mock_doc.id = "doc-1"
        mock_doc.source = "test.md"
        mock_doc.content = "Test content about Python."

        app = Mock()
        app.ask_question.return_value = "Python is a programming language."
        app.retriever.retrieve.return_value = [(mock_doc, 0.95)]

        args = Mock()
        args.question = "What is Python?"
        args.json = True

        with patch("time.time", side_effect=[0.0, 1.0]):
            result = cmd_ask(app, args)

        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)

        assert data["status"] == "success"
        assert data["question"] == "What is Python?"
        assert data["answer"] == "Python is a programming language."
        assert len(data["sources"]) == 1
        assert data["sources"][0]["document_id"] == "doc-1"
        assert data["generation_time_ms"] == 1000.0

    def test_cmd_ask_text_output(self, capsys):
        """Test ask command without --json flag."""
        app = Mock()
        app.ask_question.return_value = "Answer to the question."

        args = Mock()
        args.question = "Test question?"
        args.json = False

        with patch("time.time", return_value=0.0):
            result = cmd_ask(app, args)

        assert result == 0
        captured = capsys.readouterr()
        assert "Answer to the question." in captured.out

    def test_cmd_list_json_output_empty(self, capsys):
        """Test list command with --json flag when empty."""
        app = Mock()
        app.list_documents.return_value = []

        args = Mock()
        args.json = True

        result = cmd_list(app, args)

        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)

        assert data["status"] == "success"
        assert data["documents"] == []
        assert data["total_documents"] == 0

    def test_cmd_list_json_output_with_docs(self, capsys):
        """Test list command with --json flag with documents."""
        app = Mock()
        app.list_documents.return_value = [
            ("file1.md", 10, 5.2),
            ("file2.md", 20, 10.5),
        ]

        args = Mock()
        args.json = True

        result = cmd_list(app, args)

        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)

        assert data["status"] == "success"
        assert len(data["documents"]) == 2
        assert data["total_documents"] == 2
        assert data["total_chunks"] == 30

    def test_cmd_list_text_output_empty(self, capsys):
        """Test list command without --json flag when empty."""
        app = Mock()
        app.list_documents.return_value = []

        args = Mock()
        args.json = False

        result = cmd_list(app, args)

        assert result == 0
        captured = capsys.readouterr()
        assert "No documents imported yet." in captured.out

    def test_cmd_list_text_output_with_docs(self, capsys):
        """Test list command without --json flag with documents."""
        app = Mock()
        app.list_documents.return_value = [
            ("file1.md", 10, 5.2),
            ("file2.md", 20, 10.5),
        ]

        args = Mock()
        args.json = False

        result = cmd_list(app, args)

        assert result == 0
        captured = capsys.readouterr()
        assert "Imported documents:" in captured.out
        assert "file1.md" in captured.out
        assert "file2.md" in captured.out

    def test_cmd_delete_json_output(self, capsys):
        """Test delete command with --json flag."""
        app = Mock()

        args = Mock()
        args.doc_id = "doc-123"
        args.json = True

        result = cmd_delete(app, args)

        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)

        assert data["status"] == "success"
        assert data["deleted_document"] == "doc-123"

    def test_cmd_delete_text_output(self, capsys):
        """Test delete command without --json flag."""
        app = Mock()

        args = Mock()
        args.doc_id = "doc-456"
        args.json = False

        result = cmd_delete(app, args)

        assert result == 0
        captured = capsys.readouterr()
        assert "✓ Deleted document: doc-456" in captured.out

    def test_cmd_delete_json_error_output(self, capsys):
        """Test delete command with --json flag on error."""
        app = Mock()
        app.delete_document.side_effect = StorageError("Document not found")

        args = Mock()
        args.doc_id = "doc-999"
        args.json = True

        result = cmd_delete(app, args)

        assert result == 1
        captured = capsys.readouterr()
        data = json.loads(captured.err)

        assert data["status"] == "error"
        assert data["error_type"] == "StorageError"


class TestHandleError:
    """Tests for error handling with JSON output."""

    def test_handle_error_text_format(self, capsys):
        """Test error handler in text format."""
        from dash_ai.cli import _handle_error

        error = ValueError("Test error")
        _handle_error(error, use_json=False)

        captured = capsys.readouterr()
        assert "❌ Error: Test error" in captured.err

    def test_handle_error_json_format(self, capsys):
        """Test error handler in JSON format."""
        from dash_ai.cli import _handle_error

        error = ConfigurationError("Config not found", suggestion="Create config")
        _handle_error(error, use_json=True)

        captured = capsys.readouterr()
        data = json.loads(captured.err)

        assert data["status"] == "error"
        assert data["error_type"] == "ConfigurationError"
        assert "Config not found" in data["error_message"]
        assert data["suggestion"] == "Create config"
