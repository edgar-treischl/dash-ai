"""Document retrieval engine."""

from typing import List, Tuple

from dash_ai.core.interfaces import Document, RetrievalInterface, StorageInterface


class Retriever(RetrievalInterface):
    """Retrieve relevant documents from storage."""

    def __init__(self, storage: StorageInterface):
        """Initialize retriever.

        Args:
            storage: Storage backend for document retrieval
        """
        self.storage = storage

    def retrieve(self, query: str, top_k: int = 5) -> List[Tuple[Document, float]]:
        """Retrieve relevant documents.

        Args:
            query: Search query
            top_k: Maximum number of results

        Returns:
            List of (Document, relevance_score) tuples, score from 0.0 to 1.0
        """
        return self.storage.search(query, top_k=top_k)
