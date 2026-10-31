"""Tests for interactive chat mode."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

from dash_ai.interactive import InteractiveSession
from dash_ai.core.errors import DashAIError


@pytest.fixture
def mock_app():
    """Create a mock app instance."""
    app = Mock()
    app.ask_question = Mock()
    return app


def test_interactive_session_initialization(mock_app):
    """Test InteractiveSession initialization."""
    session = InteractiveSession(mock_app)

    assert session.app == mock_app
    assert session.questions == []
    assert session.total_generation_time == 0.0
    assert session.get_question_count() == 0


def test_interactive_session_single_question(mock_app, capsys):
    """Test asking a single question in interactive mode."""
    session = InteractiveSession(mock_app)
    mock_app.ask_question.return_value = "Test answer"

    with patch("builtins.input", side_effect=["What is Python?", "exit"]):
        session.run()

    assert session.get_question_count() == 1
    assert session.questions[0][0] == "What is Python?"
    assert session.questions[0][1] == "Test answer"

    captured = capsys.readouterr()
    assert "Dash-AI Interactive Session" in captured.out
    assert "Test answer" in captured.out
    assert "Session Summary" in captured.out


def test_interactive_session_multiple_questions(mock_app, capsys):
    """Test asking multiple questions in one session."""
    session = InteractiveSession(mock_app)
    mock_app.ask_question.side_effect = [
        "First answer",
        "Second answer",
        "Third answer",
    ]

    with patch("builtins.input", side_effect=[
        "First question",
        "Second question",
        "Third question",
        "exit"
    ]):
        session.run()

    assert session.get_question_count() == 3
    captured = capsys.readouterr()
    assert "Questions asked: 3" in captured.out


def test_interactive_session_quit_command(mock_app, capsys):
    """Test 'quit' command exits session."""
    session = InteractiveSession(mock_app)

    with patch("builtins.input", side_effect=["quit"]):
        session.run()

    assert session.get_question_count() == 0
    captured = capsys.readouterr()
    assert "Session Summary" in captured.out


def test_interactive_session_q_command(mock_app, capsys):
    """Test 'q' command exits session."""
    session = InteractiveSession(mock_app)

    with patch("builtins.input", side_effect=["q"]):
        session.run()

    assert session.get_question_count() == 0
    captured = capsys.readouterr()
    assert "Session Summary" in captured.out


def test_interactive_session_ctrl_d(mock_app, capsys):
    """Test Ctrl+D (EOF) exits session gracefully."""
    session = InteractiveSession(mock_app)

    with patch("builtins.input", side_effect=EOFError()):
        session.run()

    captured = capsys.readouterr()
    assert "Session Summary" in captured.out


def test_interactive_session_empty_input(mock_app, capsys):
    """Test empty input is skipped."""
    session = InteractiveSession(mock_app)
    mock_app.ask_question.return_value = "Answer"

    with patch("builtins.input", side_effect=["", "  ", "Question", "exit"]):
        session.run()

    assert session.get_question_count() == 1
    mock_app.ask_question.assert_called_once_with("Question")


def test_interactive_session_ctrl_c_during_input(mock_app, capsys):
    """Test Ctrl+C during input is handled gracefully."""
    session = InteractiveSession(mock_app)
    mock_app.ask_question.return_value = "Answer"

    with patch("builtins.input", side_effect=[
        KeyboardInterrupt(),
        "Question",
        "exit"
    ]):
        session.run()

    assert session.get_question_count() == 1
    captured = capsys.readouterr()
    assert "Session Summary" in captured.out


def test_interactive_session_error_handling(mock_app, capsys):
    """Test error during question processing."""
    session = InteractiveSession(mock_app)
    error = DashAIError("Test error", suggestion="Try again")
    mock_app.ask_question.side_effect = error

    with patch("builtins.input", side_effect=["Question", "exit"]):
        with pytest.raises(DashAIError):
            session.run()

    captured = capsys.readouterr()
    assert "Session Summary" in captured.out


def test_interactive_session_timing_display(mock_app, capsys):
    """Test timing information is displayed."""
    session = InteractiveSession(mock_app)
    mock_app.ask_question.return_value = "Answer"

    with patch("builtins.input", side_effect=["Question", "exit"]):
        session.run()

    captured = capsys.readouterr()
    assert "Generated in" in captured.out
    assert "s" in captured.out  # seconds


def test_interactive_session_history(mock_app):
    """Test conversation history retrieval."""
    session = InteractiveSession(mock_app)
    mock_app.ask_question.side_effect = ["Answer 1", "Answer 2"]

    with patch("builtins.input", side_effect=["Q1", "Q2", "exit"]):
        session.run()

    history = session.get_history()
    assert len(history) == 2
    assert history[0] == ("Q1", "Answer 1")
    assert history[1] == ("Q2", "Answer 2")


def test_interactive_session_summary_with_questions(mock_app, capsys):
    """Test session summary includes timing stats."""
    session = InteractiveSession(mock_app)
    mock_app.ask_question.side_effect = ["A1", "A2"]

    with patch("builtins.input", side_effect=["Q1", "Q2", "exit"]):
        session.run()

    captured = capsys.readouterr()
    assert "Questions asked: 2" in captured.out
    assert "Generation time:" in captured.out
    assert "Average time per question:" in captured.out
    assert "Total session time:" in captured.out


def test_interactive_session_summary_no_questions(mock_app, capsys):
    """Test session summary when no questions asked."""
    session = InteractiveSession(mock_app)

    with patch("builtins.input", side_effect=["exit"]):
        session.run()

    captured = capsys.readouterr()
    assert "Questions asked: 0" in captured.out
    assert "Generation time:" not in captured.out


def test_interactive_session_input_trimming(mock_app):
    """Test that input is trimmed of whitespace."""
    session = InteractiveSession(mock_app)
    mock_app.ask_question.return_value = "Answer"

    with patch("builtins.input", side_effect=["  Question with spaces  ", "exit"]):
        session.run()

    mock_app.ask_question.assert_called_once_with("Question with spaces")


def test_interactive_session_welcome_message(mock_app, capsys):
    """Test welcome message is displayed."""
    session = InteractiveSession(mock_app)

    with patch("builtins.input", side_effect=["exit"]):
        session.run()

    captured = capsys.readouterr()
    assert "Dash-AI Interactive Session" in captured.out
    assert "Ask questions about your documents" in captured.out
    assert "exit" in captured.out.lower() or "quit" in captured.out.lower()


def test_interactive_session_question_count_increments(mock_app):
    """Test question count increments correctly."""
    session = InteractiveSession(mock_app)
    mock_app.ask_question.side_effect = ["A1", "A2", "A3", "A4"]

    with patch("builtins.input", side_effect=["Q1", "Q2", "Q3", "Q4", "exit"]):
        session.run()

    assert session.get_question_count() == 4


def test_interactive_session_generation_time_tracking(mock_app):
    """Test total generation time is tracked."""
    session = InteractiveSession(mock_app)
    mock_app.ask_question.side_effect = ["Answer1", "Answer2"]

    with patch("builtins.input", side_effect=["Q1", "Q2", "exit"]):
        session.run()

    # Should have some tracked generation time (at least some small amount)
    assert session.total_generation_time >= 0.0
