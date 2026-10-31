"""Tests for CLI interface."""

import pytest
from unittest.mock import Mock, patch

from dash_ai.cli import main, cmd_ingest, cmd_ask, cmd_list, cmd_delete


def test_cli_ingest_success(capsys, tmp_path):
    """Test successful file ingestion via CLI."""
    # Create test markdown file
    md_file = tmp_path / "test.md"
    md_file.write_text("# Test\n\nContent")

    with patch("dash_ai.cli.App") as MockApp:
        mock_app = Mock()
        mock_app.ingest_files.return_value = (1, 2)
        MockApp.return_value = mock_app

        argv = ["ingest", str(md_file)]
        result = main(argv)

        assert result == 0
        captured = capsys.readouterr()
        assert "Imported 1 file" in captured.out


def test_cli_ask_success(capsys):
    """Test asking a question via CLI."""
    with patch("dash_ai.cli.App") as MockApp:
        mock_app = Mock()
        mock_app.ask_question.return_value = "Answer: Test response"
        MockApp.return_value = mock_app

        argv = ["ask", "What is test?"]
        result = main(argv)

        assert result == 0
        captured = capsys.readouterr()
        assert "Answer:" in captured.out


def test_cli_list_success(capsys):
    """Test listing documents via CLI."""
    with patch("dash_ai.cli.App") as MockApp:
        mock_app = Mock()
        mock_app.list_documents.return_value = [
            ("doc1.md", 2, 1.5),
            ("doc2.md", 3, 2.3),
        ]
        MockApp.return_value = mock_app

        result = main(["list"])

        assert result == 0
        captured = capsys.readouterr()
        assert "Imported documents:" in captured.out
        assert "doc1.md" in captured.out


def test_cli_delete_success(capsys):
    """Test deleting a document via CLI."""
    with patch("dash_ai.cli.App") as MockApp:
        mock_app = Mock()
        MockApp.return_value = mock_app

        result = main(["delete", "doc_0"])

        assert result == 0
        mock_app.delete_document.assert_called_once_with("doc_0")


def test_cli_ingest_file_not_found(capsys):
    """Test error when file not found."""
    with patch("dash_ai.cli.App") as MockApp:
        mock_app = Mock()
        mock_app.ingest_files.side_effect = FileNotFoundError("File not found")
        MockApp.return_value = mock_app

        result = main(["ingest", "nonexistent.md"])

        assert result == 1
        captured = capsys.readouterr()
        assert "Error" in captured.err


def test_cli_ask_error(capsys):
    """Test error handling during ask."""
    with patch("dash_ai.cli.App") as MockApp:
        mock_app = Mock()
        mock_app.ask_question.side_effect = RuntimeError("Model error")
        MockApp.return_value = mock_app

        result = main(["ask", "Question"])

        assert result == 1
        captured = capsys.readouterr()
        assert "Error" in captured.err


def test_cli_list_empty(capsys):
    """Test listing when no documents."""
    with patch("dash_ai.cli.App") as MockApp:
        mock_app = Mock()
        mock_app.list_documents.return_value = []
        MockApp.return_value = mock_app

        result = main(["list"])

        assert result == 0
        captured = capsys.readouterr()
        assert "No documents" in captured.out


def test_cli_delete_not_found(capsys):
    """Test error when document not found."""
    with patch("dash_ai.cli.App") as MockApp:
        mock_app = Mock()
        mock_app.delete_document.side_effect = KeyError("doc_0")
        MockApp.return_value = mock_app

        result = main(["delete", "doc_0"])

        assert result == 1
        captured = capsys.readouterr()
        assert "Error" in captured.err


def test_cli_config_error(capsys):
    """Test error when config is invalid."""
    import sys
    # Mock sys.exit to avoid actually exiting
    with patch("sys.exit") as mock_exit:
        with patch("dash_ai.cli.App") as MockApp:
            MockApp.side_effect = FileNotFoundError("config not found")

            try:
                main(["list"])
            except SystemExit:
                pass

            # Verify error was reported
            captured = capsys.readouterr()
            assert "Error" in captured.err


def test_cli_connection_error(capsys):
    """Test error when Ollama not accessible."""
    with patch("sys.exit") as mock_exit:
        with patch("dash_ai.cli.App") as MockApp:
            MockApp.side_effect = ConnectionError("Ollama not running")

            try:
                main(["ask", "test"])
            except SystemExit:
                pass

            # Verify error was reported
            captured = capsys.readouterr()
            assert "Connection error" in captured.err


def test_cli_no_command(capsys):
    """Test CLI with no command shows help."""
    with patch("dash_ai.cli.create_app"):
        result = main([])

        assert result == 1
        captured = capsys.readouterr()
        assert "usage:" in captured.out.lower()
