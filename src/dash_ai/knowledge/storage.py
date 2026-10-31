"""SQLite storage backend for documents."""

import json
import re
import sqlite3
from pathlib import Path
from typing import List, Tuple

from dash_ai.core.interfaces import Document, StorageInterface


class SQLiteStorage(StorageInterface):
    """Store documents in SQLite with full-text search indexing."""

    def __init__(self, db_path: str):
        """Initialize SQLite storage.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize database on first run
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Create documents table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    source TEXT NOT NULL,
                    format TEXT NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            # Create FTS5 virtual table for full-text search
            cursor.execute(
                """
                CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
                    id UNINDEXED,
                    title,
                    content,
                    tokenize = 'porter'
                )
                """
            )

            conn.commit()

    def save_document(self, doc: Document) -> None:
        """Save document to storage.

        Args:
            doc: Document to save
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            metadata_json = json.dumps(doc.metadata)

            # Insert or replace in main table
            cursor.execute(
                """
                INSERT OR REPLACE INTO documents
                (id, title, content, source, format, metadata, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """,
                (doc.id, doc.title, doc.content, doc.source, doc.format, metadata_json),
            )

            # Delete from FTS index if exists (to avoid duplicates)
            cursor.execute("DELETE FROM documents_fts WHERE id = ?", (doc.id,))

            # Insert into FTS index
            cursor.execute(
                "INSERT INTO documents_fts (id, title, content) VALUES (?, ?, ?)",
                (doc.id, doc.title, doc.content),
            )

            conn.commit()

    def get_document(self, doc_id: str) -> Document:
        """Retrieve document by ID.

        Args:
            doc_id: Document identifier

        Returns:
            Document object

        Raises:
            KeyError: If document not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, title, content, source, format, metadata
                FROM documents WHERE id = ?
                """,
                (doc_id,),
            )
            row = cursor.fetchone()

        if not row:
            raise KeyError(f"Document not found: {doc_id}")

        doc_id, title, content, source, format_, metadata_json = row
        metadata = json.loads(metadata_json) if metadata_json else {}

        return Document(
            id=doc_id,
            title=title,
            content=content,
            source=source,
            format=format_,
            metadata=metadata,
        )

    def list_documents(self) -> List[Document]:
        """List all stored documents.

        Returns:
            List of all documents
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, title, content, source, format, metadata
                FROM documents ORDER BY created_at DESC
                """
            )
            rows = cursor.fetchall()

        documents = []
        for row in rows:
            doc_id, title, content, source, format_, metadata_json = row
            metadata = json.loads(metadata_json) if metadata_json else {}
            doc = Document(
                id=doc_id,
                title=title,
                content=content,
                source=source,
                format=format_,
                metadata=metadata,
            )
            documents.append(doc)

        return documents

    def search(self, query: str, top_k: int = 5) -> List[Tuple[Document, float]]:
        """Full-text search with relevance scoring.

        Args:
            query: Plain-text query; results match any word
            top_k: Maximum number of results

        Returns:
            List of (Document, relevance_score) tuples, score from 0.0 to 1.0
        """
        terms = re.findall(r"[^\W_]+", query)
        if not terms:
            return []
        fts_query = " OR ".join(f'"{term}"' for term in terms)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # FTS5 search with ranking
            query_sql = """
                SELECT
                    d.id, d.title, d.content, d.source, d.format, d.metadata,
                    fts.rank
                FROM documents_fts fts
                JOIN documents d ON fts.id = d.id
                WHERE documents_fts MATCH ?
                ORDER BY fts.rank
                LIMIT ?
                """
            cursor.execute(query_sql, (fts_query, top_k))
            rows = cursor.fetchall()

        if not rows:
            return []

        # Normalize scores (FTS5 rank is negative, closer to 0 is better)
        results = []
        for row in rows:
            doc_id, title, content, source, format_, metadata_json, rank_score = row
            metadata = json.loads(metadata_json) if metadata_json else {}

            doc = Document(
                id=doc_id,
                title=title,
                content=content,
                source=source,
                format=format_,
                metadata=metadata,
            )

            # Normalize score: FTS5 rank is negative (e.g., -0.5)
            # Convert to 0.0-1.0 scale where 1.0 is best match
            if rank_score < 0:
                # score = 1 / (1 + abs(rank_score)) gives 0-1 scale
                score = 1.0 / (1.0 + abs(rank_score))
            else:
                score = 1.0

            results.append((doc, score))

        return results

    def delete_document(self, doc_id: str) -> None:
        """Delete document by ID.

        Args:
            doc_id: Document identifier to delete

        Raises:
            KeyError: If document not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Check if document exists
            cursor.execute("SELECT id FROM documents WHERE id = ?", (doc_id,))
            if not cursor.fetchone():
                raise KeyError(f"Document not found: {doc_id}")

            # Delete from both tables
            cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
            cursor.execute("DELETE FROM documents_fts WHERE id = ?", (doc_id,))

            conn.commit()
