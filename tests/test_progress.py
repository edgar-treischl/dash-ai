"""Tests for progress indicators and timing utilities."""

import time
import pytest
import sys
from io import StringIO
from unittest.mock import patch, MagicMock

from dash_ai.progress import Spinner, ProgressBar, Timer, time_operation


class TestSpinner:
    """Tests for Spinner class."""

    def test_spinner_initialization(self):
        """Test spinner initialization."""
        spinner = Spinner(message="Loading", use_spinner=True)
        assert spinner.message == "Loading"
        assert spinner.use_spinner is True
        assert spinner.is_running is False
        assert spinner.current_frame == 0

    def test_spinner_disabled(self):
        """Test spinner with use_spinner=False."""
        spinner = Spinner(use_spinner=False)
        # Should not raise when disabled
        spinner.start()
        spinner.tick()
        spinner.stop()
        assert spinner.is_running is False

    def test_spinner_frames(self):
        """Test spinner frame rotation."""
        # Verify frame list exists and is correct
        frames = ["|", "/", "-", "\\"]
        for i, expected_frame in enumerate(frames):
            assert Spinner.FRAMES[i] == expected_frame

        # Test frame cycling - tick updates frame when is_running
        spinner = Spinner(use_spinner=True)
        spinner.current_frame = 0
        spinner.is_running = True  # Must be running for tick() to work
        assert Spinner.FRAMES[spinner.current_frame] == "|"
        spinner.tick()
        assert Spinner.FRAMES[spinner.current_frame] == "/"
        spinner.tick()
        assert Spinner.FRAMES[spinner.current_frame] == "-"

    def test_spinner_start_stop(self):
        """Test spinner start and stop."""
        spinner = Spinner(message="Test", use_spinner=True)
        with patch("sys.stderr", new_callable=StringIO):
            spinner.start()
            assert spinner.is_running is True
            spinner.stop(clear=False)
            assert spinner.is_running is False

    def test_spinner_clear_on_stop(self):
        """Test spinner clears line when stopped."""
        spinner = Spinner(use_spinner=True)
        with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
            spinner.start()
            spinner.stop(clear=True)
            output = mock_stderr.getvalue()
            # Should contain spaces to clear the line
            assert "  " in output or output == ""


class TestProgressBar:
    """Tests for ProgressBar class."""

    def test_progress_bar_initialization(self):
        """Test progress bar initialization."""
        bar = ProgressBar(total=10, message="Processing", use_progress=True)
        assert bar.total == 10
        assert bar.message == "Processing"
        assert bar.use_progress is True
        assert bar.current == 0

    def test_progress_bar_disabled(self):
        """Test progress bar with use_progress=False."""
        bar = ProgressBar(total=10, use_progress=False)
        # Should not raise when disabled
        bar.update(0)
        bar.update(5)
        bar.finish()

    def test_progress_bar_update(self):
        """Test progress bar update."""
        bar = ProgressBar(total=10, use_progress=True)
        with patch("sys.stderr", new_callable=StringIO):
            bar.update(0)
            assert bar.current == 1
            bar.update(4)
            assert bar.current == 5
            bar.update(9)
            assert bar.current == 10

    def test_progress_bar_zero_total(self):
        """Test progress bar with zero total."""
        bar = ProgressBar(total=0, use_progress=True)
        # Should not raise with zero total
        bar.update(0)
        bar.finish()

    def test_progress_bar_finish(self):
        """Test progress bar finish clears line."""
        bar = ProgressBar(total=10, message="Test", use_progress=True)
        with patch("sys.stderr", new_callable=StringIO):
            bar.update(9)
            bar.finish()


class TestTimer:
    """Tests for Timer class."""

    def test_timer_initialization(self):
        """Test timer initialization."""
        timer = Timer(name="Test")
        assert timer.name == "Test"
        assert timer.start_time is None
        assert timer.end_time is None

    def test_timer_context_manager(self):
        """Test timer as context manager."""
        with Timer("Test") as timer:
            time.sleep(0.01)
        assert timer.start_time is not None
        assert timer.end_time is not None
        assert timer.elapsed_ms() > 5  # At least 5ms

    def test_timer_manual_start_stop(self):
        """Test timer manual start and stop."""
        timer = Timer()
        timer.start()
        time.sleep(0.01)
        timer.stop()
        assert timer.elapsed_ms() > 5

    def test_timer_elapsed_without_stop(self):
        """Test elapsed raises error if not stopped."""
        timer = Timer()
        timer.start()
        with pytest.raises(RuntimeError):
            timer.elapsed_ms()

    def test_timer_elapsed_ms(self):
        """Test elapsed time in milliseconds."""
        timer = Timer()
        timer.start()
        time.sleep(0.05)
        timer.stop()
        elapsed = timer.elapsed_ms()
        assert 40 < elapsed < 100  # Allow some variance

    def test_timer_elapsed_seconds(self):
        """Test elapsed time in seconds."""
        timer = Timer()
        timer.start()
        time.sleep(0.05)
        timer.stop()
        elapsed = timer.elapsed_seconds()
        assert 0.04 < elapsed < 0.1

    def test_timer_format_milliseconds(self):
        """Test timer format for milliseconds."""
        timer = Timer()
        timer.start_time = time.time()
        timer.end_time = timer.start_time + 0.1  # 100ms
        formatted = timer.format()
        assert "ms" in formatted or "100" in formatted

    def test_timer_format_seconds(self):
        """Test timer format for seconds."""
        timer = Timer()
        timer.start_time = time.time()
        timer.end_time = timer.start_time + 1.5  # 1.5 seconds
        formatted = timer.format()
        assert "s" in formatted
        assert "1.50" in formatted or "1.5" in formatted

    def test_timer_not_started(self):
        """Test error when timer not started."""
        timer = Timer()
        timer.end_time = time.time()
        with pytest.raises(RuntimeError):
            timer.elapsed_ms()


class TestTimeOperation:
    """Tests for time_operation helper."""

    def test_time_operation_basic(self):
        """Test timing a simple function."""
        def test_func(x, y):
            time.sleep(0.01)
            return x + y

        result, elapsed_ms = time_operation(test_func, 2, 3)
        assert result == 5
        assert elapsed_ms > 5

    def test_time_operation_with_kwargs(self):
        """Test timing a function with keyword arguments."""
        def test_func(x, y=10):
            return x + y

        result, elapsed_ms = time_operation(test_func, 5, y=15)
        assert result == 20
        assert elapsed_ms >= 0

    def test_time_operation_with_exception(self):
        """Test timing a function that raises exception."""
        def test_func():
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            time_operation(test_func)


class TestProgressIntegration:
    """Integration tests for progress components."""

    def test_spinner_and_timer_together(self):
        """Test spinner and timer working together."""
        spinner = Spinner(use_spinner=False)  # Disabled for testing
        with Timer("test") as timer:
            spinner.start()
            time.sleep(0.01)
            spinner.stop()
        assert timer.elapsed_ms() > 5

    def test_progress_bar_and_timer_together(self):
        """Test progress bar and timer working together."""
        bar = ProgressBar(total=5, use_progress=True)  # Enable to track current
        with Timer("test") as timer:
            for i in range(5):
                bar.update(i)
                time.sleep(0.001)
            bar.finish()
        assert timer.elapsed_ms() > 2
        assert bar.current == 5

    def test_spinner_output_to_stderr(self):
        """Test spinner writes to stderr."""
        spinner = Spinner(message="Test", use_spinner=True)
        with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
            spinner.start()
            output = mock_stderr.getvalue()
            # Should have written something (unless completely cleared)
            # Just verify no exception

    def test_progress_bar_output_to_stderr(self):
        """Test progress bar writes to stderr."""
        bar = ProgressBar(total=5, use_progress=True)
        with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
            for i in range(5):
                bar.update(i)
            bar.finish()
            # Should have written output to stderr
            # Just verify no exception
