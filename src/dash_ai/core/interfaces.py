"""Abstract interfaces for pluggable components."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class Document:
    """Common internal document representation."""
    id: str
    title: str
    content: str
    source: str  # "file.md"
    format: str  # "markdown"
    metadata: dict = field(default_factory=dict)


class ModelInterface(ABC):
    """Abstract interface for LLM models."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate response from prompt.

        Args:
            prompt: Input text for the model

        Returns:
            Generated text response
        """
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """Return model identifier.

        Returns:
            Model name/identifier
        """
        pass


class ReaderInterface(ABC):
    """Abstract interface for input format readers."""

    @abstractmethod
    def read(self, file_path: str) -> List[Document]:
        """Read file and return list of Document chunks.

        Args:
            file_path: Path to file to read

        Returns:
            List of Document objects, one per chunk
        """
        pass

    @abstractmethod
    def supports_format(self, file_path: str) -> bool:
        """Check if reader handles this format.

        Args:
            file_path: Path to file to check

        Returns:
            True if reader can handle this file format
        """
        pass


class StorageInterface(ABC):
    """Abstract interface for document storage."""

    @abstractmethod
    def save_document(self, doc: Document) -> None:
        """Save document to storage.

        Args:
            doc: Document to save
        """
        pass

    @abstractmethod
    def get_document(self, doc_id: str) -> Document:
        """Retrieve document by ID.

        Args:
            doc_id: Document identifier

        Returns:
            Document object

        Raises:
            KeyError: If document not found
        """
        pass

    @abstractmethod
    def list_documents(self) -> List[Document]:
        """List all stored documents.

        Returns:
            List of all documents
        """
        pass

    @abstractmethod
    def search(self, query: str, top_k: int = 5) -> List[Tuple[Document, float]]:
        """Full-text search.

        Args:
            query: Search query
            top_k: Maximum number of results

        Returns:
            List of (Document, relevance_score) tuples, score from 0.0 to 1.0
        """
        pass

    @abstractmethod
    def delete_document(self, doc_id: str) -> None:
        """Delete document by ID.

        Args:
            doc_id: Document identifier to delete

        Raises:
            KeyError: If document not found
        """
        pass


class RetrievalInterface(ABC):
    """Abstract interface for retrieval."""

    @abstractmethod
    def retrieve(self, query: str, top_k: int = 5) -> List[Tuple[Document, float]]:
        """Retrieve relevant documents.

        Args:
            query: Search query
            top_k: Maximum number of results

        Returns:
            List of (Document, relevance_score) tuples, score from 0.0 to 1.0
        """
        pass
