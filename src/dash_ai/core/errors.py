"""Custom exceptions for Dash-AI."""


class DashAIError(Exception):
    """Base exception for all Dash-AI errors."""

    def __init__(self, message: str, suggestion: str | None = None) -> None:
        """Initialize the error with a message and optional recovery suggestion.

        Args:
            message: The error message to display to the user.
            suggestion: Optional recovery suggestion (e.g., "Is Ollama running?").
        """
        self.message = message
        self.suggestion = suggestion
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """Format the error message with optional suggestion."""
        if self.suggestion:
            return f"{self.message}\n💡 Tip: {self.suggestion}"
        return self.message


class ConfigurationError(DashAIError):
    """Configuration is invalid or missing."""

    pass


class StorageError(DashAIError):
    """Database or storage operation failed."""

    pass


class ModelError(DashAIError):
    """LLM or model operation failed."""

    pass


class RetrievalError(DashAIError):
    """Document retrieval operation failed."""

    pass


class IngestionError(DashAIError):
    """Document ingestion operation failed."""

    pass
