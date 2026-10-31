"""JSON output formatting for dash-ai CLI commands."""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from dash_ai.core.interfaces import Document


class JSONFormatter:
    """Formats command output to JSON."""

    @staticmethod
    def ingest_success(num_files: int, num_chunks: int) -> str:
        """Format successful ingestion response.

        Args:
            num_files: Number of files imported
            num_chunks: Total number of chunks created

        Returns:
            JSON string
        """
        response = {
            "status": "success",
            "files_imported": num_files,
            "chunks_created": num_chunks,
        }
        return json.dumps(response, indent=2)

    @staticmethod
    def ask_success(
        question: str,
        answer: str,
        sources: List[Tuple[Document, float]],
        generation_time_ms: float,
    ) -> str:
        """Format successful question-answer response.

        Args:
            question: The question asked
            answer: The generated answer
            sources: List of (Document, relevance_score) tuples
            generation_time_ms: Time taken to generate answer in milliseconds

        Returns:
            JSON string
        """
        source_list = []
        for doc, score in sources:
            source_list.append({
                "document_id": doc.id,
                "source_file": doc.source,
                "relevance_score": round(score, 3),
                "excerpt": doc.content[:200] + "..." if len(doc.content) > 200 else doc.content,
            })

        response = {
            "status": "success",
            "question": question,
            "answer": answer,
            "sources": source_list,
            "generation_time_ms": round(generation_time_ms, 2),
        }
        return json.dumps(response, indent=2)

    @staticmethod
    def list_success(documents: List[Tuple[str, int, float]]) -> str:
        """Format list documents response.

        Args:
            documents: List of (source, chunk_count, size_kb) tuples

        Returns:
            JSON string
        """
        doc_list = []
        for source, chunks, size_kb in documents:
            doc_list.append({
                "source": source,
                "chunks": chunks,
                "size_kb": round(size_kb, 1),
            })

        response = {
            "status": "success",
            "documents": doc_list,
            "total_documents": len(doc_list),
            "total_chunks": sum(d["chunks"] for d in doc_list),
        }
        return json.dumps(response, indent=2)

    @staticmethod
    def delete_success(doc_id: str) -> str:
        """Format successful delete response.

        Args:
            doc_id: ID of deleted document

        Returns:
            JSON string
        """
        response = {
            "status": "success",
            "deleted_document": doc_id,
        }
        return json.dumps(response, indent=2)

    @staticmethod
    def error(
        error_message: str,
        error_type: str,
        suggestion: Optional[str] = None,
    ) -> str:
        """Format error response.

        Args:
            error_message: Human-readable error message
            error_type: Type of error (e.g., ConfigurationError)
            suggestion: Optional recovery suggestion

        Returns:
            JSON string
        """
        response = {
            "status": "error",
            "error_type": error_type,
            "error_message": error_message,
        }

        if suggestion:
            response["suggestion"] = suggestion

        return json.dumps(response, indent=2)

    @staticmethod
    def success_response(data: Dict[str, Any]) -> str:
        """Format a generic success response.

        Args:
            data: Data to include in response

        Returns:
            JSON string with status=success and data
        """
        response = {"status": "success", **data}
        return json.dumps(response, indent=2)

    @staticmethod
    def error_response(
        message: str,
        error_type: str = "Error",
        suggestion: Optional[str] = None,
    ) -> str:
        """Format a generic error response.

        Args:
            message: Error message
            error_type: Type of error
            suggestion: Optional recovery suggestion

        Returns:
            JSON string
        """
        response = {
            "status": "error",
            "error_type": error_type,
            "error_message": message,
        }

        if suggestion:
            response["suggestion"] = suggestion

        return json.dumps(response, indent=2)
