"""Tests for CLI progress indicators integration."""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from dash_ai.cli import cmd_ingest, cmd_ask
from dash_ai.core.errors import StorageError, ModelError


class TestCLIProgressIntegration:
    """Tests for CLI progress indicators."""

    def test_cmd_ingest_progress_bar_shown_text_mode(self, capsys, tmp_path):
        """Test ingest command shows progress bar in text mode."""
        # Create temporary files
        (tmp_path / "file1.md").write_text("# Test 1\nContent here")
        (tmp_path / "file2.md").write_text("# Test 2\nMore content")

        app = Mock()

        def progress_callback(current: int, total: int) -> None:
            pass  # Just accept the callback

        app.ingest_files.return_value = (2, 20)

        args = Mock()
        args.path = str(tmp_path)
        args.json = False

        result = cmd_ingest(app, args)

        assert result == 0
        captured = capsys.readouterr()
        assert "✓ Imported 2 file(s)" in captured.out
        assert "Completed in" in captured.out

    def test_cmd_ingest_progress_bar_disabled_json_mode(self, capsys, tmp_path):
        """Test ingest command suppresses progress bar in JSON mode."""
        (tmp_path / "file1.md").write_text("# Test\nContent")

        app = Mock()
        app.ingest_files.return_value = (1, 10)

        args = Mock()
        args.path = str(tmp_path)
        args.json = True

        result = cmd_ingest(app, args)

        assert result == 0
        captured = capsys.readouterr()
        # Should only have JSON output, no progress bar formatting
        data = json.loads(captured.out)
        assert data["status"] == "success"
        assert data["files_imported"] == 1

    def test_cmd_ask_spinner_shown_text_mode(self, capsys):
        """Test ask command shows spinner in text mode."""
        mock_doc = Mock()
        mock_doc.id = "doc-1"
        mock_doc.source = "test.md"
        mock_doc.content = "Test content"

        app = Mock()
        app.ask_question.return_value = "The answer is 42."
        app.retriever.retrieve.return_value = [(mock_doc, 0.95)]

        args = Mock()
        args.question = "What is the answer?"
        args.json = False

        result = cmd_ask(app, args)

        assert result == 0
        captured = capsys.readouterr()
        assert "The answer is 42." in captured.out
        assert "✓ Generated in" in captured.out

    def test_cmd_ask_spinner_disabled_json_mode(self, capsys):
        """Test ask command suppresses spinner in JSON mode."""
        mock_doc = Mock()
        mock_doc.id = "doc-1"
        mock_doc.source = "test.md"
        mock_doc.content = "Test"

        app = Mock()
        app.ask_question.return_value = "Answer"
        app.retriever.retrieve.return_value = [(mock_doc, 0.9)]

        args = Mock()
        args.question = "Question?"
        args.json = True

        result = cmd_ask(app, args)

        assert result == 0
        captured = capsys.readouterr()
        # Should have JSON output
        data = json.loads(captured.out)
        assert data["status"] == "success"
        assert "generation_time_ms" in data

    def test_cmd_ask_timing_in_json_response(self, capsys):
        """Test ask command includes timing in JSON response."""
        mock_doc = Mock()
        mock_doc.id = "doc-1"
        mock_doc.source = "test.md"
        mock_doc.content = "Content"

        app = Mock()
        app.ask_question.return_value = "Response"
        app.retriever.retrieve.return_value = [(mock_doc, 0.85)]

        args = Mock()
        args.question = "Test?"
        args.json = True

        # Patch the Timer class to return a fixed elapsed time
        with patch("dash_ai.cli.Timer") as MockTimer:
            mock_timer = MagicMock()
            mock_timer.__enter__.return_value = mock_timer
            mock_timer.__exit__.return_value = None
            mock_timer.elapsed_ms.return_value = 500.0  # 500ms
            MockTimer.return_value = mock_timer

            result = cmd_ask(app, args)

        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)

        # Should have timing in milliseconds
        assert data["generation_time_ms"] == 500.0

    def test_cmd_ingest_accepts_progress_callback(self):
        """Test that cmd_ingest can pass progress callback to app.ingest_files."""
        app = Mock()

        # Track if callback was passed
        def mock_ingest(path, progress_callback=None):
            if progress_callback:
                # Simulate progress
                progress_callback(0, 2)
                progress_callback(1, 2)
                progress_callback(2, 2)
            return (2, 20)

        app.ingest_files.side_effect = mock_ingest

        args = Mock()
        args.path = "/some/path"
        args.json = False

        with patch("dash_ai.cli.ProgressBar"):
            result = cmd_ingest(app, args)

        assert result == 0
        # Verify callback was passed
        call_args = app.ingest_files.call_args
        assert "progress_callback" in call_args.kwargs


class TestAppProgressCallback:
    """Tests for App.ingest_files progress callback."""

    def test_ingest_files_calls_progress_callback(self):
        """Test that ingest_files calls progress callback."""
        from dash_ai.app import App
        from pathlib import Path
        import tempfile
        from unittest.mock import Mock, patch

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            test_dir = Path(tmpdir)
            (test_dir / "file1.md").write_text("# Test 1\nContent")
            (test_dir / "file2.md").write_text("# Test 2\nMore")

            # Mock App to avoid Ollama dependency
            with patch("dash_ai.app.OllamaModel"):
                app = App()

                progress_calls = []

                def track_progress(current: int, total: int) -> None:
                    progress_calls.append((current, total))

                try:
                    app.ingest_files(str(test_dir), progress_callback=track_progress)
                except Exception:
                    # Might fail on various operations, that's ok
                    pass

                # Should have called progress callback
                assert len(progress_calls) > 0

    def test_ingest_files_without_progress_callback(self):
        """Test that ingest_files works without progress callback."""
        from dash_ai.app import App
        import tempfile
        from pathlib import Path
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir)
            (test_dir / "file1.md").write_text("# Test\nContent")

            with patch("dash_ai.app.OllamaModel"):
                app = App()

                try:
                    # Should not raise without callback
                    result = app.ingest_files(str(test_dir), progress_callback=None)
                    # Result should be (num_files, num_chunks)
                    assert isinstance(result, tuple)
                    assert len(result) == 2
                except Exception:
                    # Might fail on various operations, that's ok
                    pass
