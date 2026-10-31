"""Application layer coordinating all components."""

from pathlib import Path
from typing import List, Optional, Tuple

from dash_ai.answering.engine import AnsweringEngine
from dash_ai.answering.retrieval import Retriever
from dash_ai.core.config import Config
from dash_ai.core.interfaces import Document, ModelInterface, ReaderInterface, StorageInterface
from dash_ai.ingestion.markdown import MarkdownReader
from dash_ai.knowledge.storage import SQLiteStorage
from dash_ai.models.ollama import OllamaModel


class App:
    """Main application coordinator."""

    def __init__(self, config_file: str = "config/settings.yaml"):
        """Initialize application with all components.

        Args:
            config_file: Path to configuration file

        Raises:
            FileNotFoundError: If config file not found
            ValueError: If configuration invalid
            ConnectionError: If Ollama not accessible
        """
        # Load config
        self.config = Config(config_file)

        # Initialize storage
        storage_path = self.config.get("storage", "path")
        self.storage: StorageInterface = SQLiteStorage(storage_path)

        # Initialize model
        model_host = self.config.get("model", "host")
        model_name = self.config.get("model", "name")
        self.model: ModelInterface = OllamaModel(model_host, model_name)

        # Initialize retriever
        self.retriever = Retriever(self.storage)

        # Initialize answering engine
        self.engine = AnsweringEngine(self.retriever, self.model)

        # Initialize readers
        self.readers = {
            "markdown": MarkdownReader(),
        }

    def ingest_files(self, path: str) -> Tuple[int, int]:
        """Ingest files (Markdown) into storage.

        Args:
            path: File or directory path

        Returns:
            Tuple of (documents_imported, total_chunks)

        Raises:
            FileNotFoundError: If path not found
            ValueError: If no supported files found
        """
        file_path = Path(path)

        if not file_path.exists():
            raise FileNotFoundError(f"Path not found: {path}")

        files_to_ingest = []

        # Collect files
        if file_path.is_file():
            files_to_ingest.append(file_path)
        else:
            # Recursively find Markdown files
            files_to_ingest.extend(file_path.glob("**/*.md"))
            files_to_ingest.extend(file_path.glob("**/*.markdown"))

        if not files_to_ingest:
            raise ValueError(f"No Markdown files found in: {path}")

        # Ingest files
        total_docs = 0
        total_chunks = 0

        for file_path in files_to_ingest:
            reader = self.readers["markdown"]
            documents = reader.read(str(file_path))

            for doc in documents:
                self.storage.save_document(doc)
                total_docs += 1
                total_chunks += 1

        return len(files_to_ingest), total_chunks

    def ask_question(self, question: str, top_k: Optional[int] = None) -> str:
        """Ask a question and get an answer with sources.

        Args:
            question: User question
            top_k: Number of documents to retrieve (uses config default if None)

        Returns:
            Formatted answer with sources
        """
        if top_k is None:
            top_k = self.config.get("retrieval", "top_k", 5)

        answer, _ = self.engine.answer(question, top_k=top_k)
        return answer

    def list_documents(self) -> List[Tuple[str, int, int]]:
        """List all imported documents.

        Returns:
            List of (source, chunk_count, size_kb) tuples
        """
        documents = self.storage.list_documents()

        # Group by source to count chunks
        sources = {}
        for doc in documents:
            source = doc.source
            if source not in sources:
                sources[source] = {
                    "chunks": 0,
                    "size_bytes": 0,
                }
            sources[source]["chunks"] += 1
            sources[source]["size_bytes"] += len(doc.content)

        # Format results
        results = []
        for source, info in sources.items():
            size_kb = info["size_bytes"] / 1024
            results.append((source, info["chunks"], size_kb))

        return results

    def delete_document(self, doc_id: str) -> None:
        """Delete a document.

        Args:
            doc_id: Document identifier

        Raises:
            KeyError: If document not found
        """
        self.storage.delete_document(doc_id)

    def get_document(self, doc_id: str) -> Document:
        """Retrieve a specific document.

        Args:
            doc_id: Document identifier

        Returns:
            Document object

        Raises:
            KeyError: If document not found
        """
        return self.storage.get_document(doc_id)
