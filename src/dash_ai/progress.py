"""Progress indicators and timing utilities for dash-ai CLI."""

import sys
import time
from typing import Optional, Callable, Any


class Spinner:
    """Simple ASCII spinner for long-running operations."""

    FRAMES = ["|", "/", "-", "\\"]

    def __init__(self, message: str = "Thinking", use_spinner: bool = True):
        """Initialize spinner.

        Args:
            message: Message to display next to spinner
            use_spinner: If False, spinner is disabled (for --json mode)
        """
        self.message = message
        self.use_spinner = use_spinner
        self.current_frame = 0
        self.is_running = False

    def start(self) -> None:
        """Start the spinner."""
        if not self.use_spinner:
            return
        self.is_running = True
        self.current_frame = 0
        self._draw()

    def stop(self, clear: bool = True) -> None:
        """Stop the spinner.

        Args:
            clear: If True, clear the spinner line from terminal
        """
        if not self.use_spinner or not self.is_running:
            return
        self.is_running = False
        if clear:
            # Clear the line with spaces and return to start
            sys.stderr.write("\r" + " " * (len(self.message) + 4) + "\r")
            sys.stderr.flush()

    def tick(self) -> None:
        """Update spinner to next frame."""
        if not self.use_spinner or not self.is_running:
            return
        self.current_frame = (self.current_frame + 1) % len(self.FRAMES)
        self._draw()

    def _draw(self) -> None:
        """Draw the current spinner frame."""
        frame = self.FRAMES[self.current_frame]
        sys.stderr.write(f"\r{frame} {self.message}... ")
        sys.stderr.flush()


class ProgressBar:
    """Simple progress bar for batch operations."""

    def __init__(
        self,
        total: int,
        message: str = "Processing",
        use_progress: bool = True,
        bar_width: int = 20,
    ):
        """Initialize progress bar.

        Args:
            total: Total number of items to process
            message: Message to display
            use_progress: If False, progress bar is disabled
            bar_width: Width of progress bar in characters
        """
        self.total = total
        self.message = message
        self.use_progress = use_progress
        self.bar_width = bar_width
        self.current = 0

    def update(self, current: int) -> None:
        """Update progress bar.

        Args:
            current: Current item number (0-based)
        """
        if not self.use_progress or self.total == 0:
            return

        self.current = current + 1
        percentage = self.current / self.total
        filled = int(self.bar_width * percentage)
        bar = "█" * filled + "░" * (self.bar_width - filled)

        # Display progress bar
        sys.stderr.write(
            f"\r{self.message}: [{bar}] {self.current}/{self.total}"
        )
        sys.stderr.flush()

    def finish(self) -> None:
        """Finish progress bar and clear line."""
        if not self.use_progress:
            return
        # Clear the progress bar line
        sys.stderr.write("\r" + " " * (len(self.message) + self.bar_width + 15) + "\r")
        sys.stderr.flush()


class Timer:
    """Simple timer for measuring operation duration."""

    def __init__(self, name: str = "Operation"):
        """Initialize timer.

        Args:
            name: Name of operation being timed
        """
        self.name = name
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None

    def __enter__(self) -> "Timer":
        """Enter context manager."""
        self.start()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context manager."""
        self.stop()

    def start(self) -> None:
        """Start the timer."""
        self.start_time = time.time()
        self.end_time = None

    def stop(self) -> None:
        """Stop the timer."""
        self.end_time = time.time()

    def elapsed_ms(self) -> float:
        """Get elapsed time in milliseconds.

        Returns:
            Elapsed time in milliseconds

        Raises:
            RuntimeError: If timer not stopped
        """
        if self.start_time is None or self.end_time is None:
            raise RuntimeError("Timer not properly started/stopped")
        return (self.end_time - self.start_time) * 1000

    def elapsed_seconds(self) -> float:
        """Get elapsed time in seconds.

        Returns:
            Elapsed time in seconds

        Raises:
            RuntimeError: If timer not stopped
        """
        return self.elapsed_ms() / 1000

    def format(self) -> str:
        """Get formatted elapsed time string.

        Returns:
            Formatted time (e.g., "1.23s", "456ms")

        Raises:
            RuntimeError: If timer not stopped
        """
        ms = self.elapsed_ms()
        if ms >= 1000:
            return f"{ms / 1000:.2f}s"
        else:
            return f"{ms:.0f}ms"


def time_operation(func: Callable, *args: Any, **kwargs: Any) -> tuple:
    """Time a function call and return result with elapsed time.

    Args:
        func: Function to call
        *args: Positional arguments to pass to function
        **kwargs: Keyword arguments to pass to function

    Returns:
        Tuple of (result, elapsed_ms)
    """
    timer = Timer()
    timer.start()
    result = func(*args, **kwargs)
    timer.stop()
    return result, timer.elapsed_ms()
