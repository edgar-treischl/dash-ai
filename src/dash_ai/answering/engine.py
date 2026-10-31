"""Question-answering engine combining retrieval and generation."""

from typing import List, Tuple

from dash_ai.core.config import Config
from dash_ai.core.interfaces import Document, ModelInterface, RetrievalInterface


class AnsweringEngine:
    """Orchestrate document retrieval and model generation for Q&A."""

    def __init__(
        self, retriever: RetrievalInterface, model: ModelInterface, config: Config | None = None
    ):
        """Initialize answering engine.

        Args:
            retriever: Retrieval backend for finding relevant documents
            model: Language model for generating answers
            config: Optional configuration for language settings
        """
        self.retriever = retriever
        self.model = model
        self.config = config or Config()
        self.language = self.config.get("app", "language") or "English"

    def answer(self, question: str, top_k: int = 5) -> Tuple[str, List[Document]]:
        """Answer a question using RAG (retrieval-augmented generation).

        Args:
            question: User question
            top_k: Maximum documents to retrieve

        Returns:
            Tuple of (answer_text, source_documents)
        """
        # Retrieve relevant documents
        results = self.retriever.retrieve(question, top_k=top_k)

        if not results:
            return (
                "I couldn't find any relevant information to answer your question.",
                [],
            )

        # Extract documents and build context
        source_docs = [doc for doc, _ in results]
        context = self._build_context(source_docs)

        # Build RAG prompt
        prompt = self._build_prompt(question, context)

        # Generate answer
        response = self.model.generate(prompt)

        # Format answer with sources
        formatted_answer = self._format_answer(response, source_docs)

        return formatted_answer, source_docs

    def _build_context(self, documents: List[Document]) -> str:
        """Build context string from retrieved documents.

        Args:
            documents: List of relevant documents

        Returns:
            Formatted context string
        """
        context_parts = []
        for doc in documents:
            context_parts.append(f"[{doc.source}]\n{doc.content}")

        return "\n\n---\n\n".join(context_parts)

    def _build_prompt(self, question: str, context: str) -> str:
        """Build RAG prompt for the model.

        Args:
            question: User question
            context: Retrieved document context

        Returns:
            Formatted prompt
        """
        return f"""Based on the following information:

{context}

Answer this question in {self.language}: {question}"""

    def _format_answer(self, answer: str, documents: List[Document]) -> str:
        """Format answer with source references.

        Args:
            answer: Generated answer text
            documents: Source documents

        Returns:
            Formatted answer with sources
        """
        formatted = f"Answer: {answer}\n\nSources:\n"

        for doc in documents:
            chunk_idx = doc.metadata.get("chunk_index", 0)
            formatted += f"- {doc.source} (chunk {chunk_idx})\n"

        return formatted
