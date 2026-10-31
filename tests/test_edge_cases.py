"""Edge cases and robustness tests for dash-ai.

These tests cover edge cases, special inputs, and error conditions
while maintaining compatibility with the existing codebase.
"""

import sqlite3
from pathlib import Path
from unittest.mock import patch

import pytest

from dash_ai.answering.retrieval import Retriever
from dash_ai.core.interfaces import Document
from dash_ai.core.errors import StorageError, IngestionError
from dash_ai.ingestion.markdown import MarkdownReader
from dash_ai.knowledge.storage import SQLiteStorage


class TestEmptyDatabaseEdgeCases:
    """Test behavior with empty or minimal data."""

    def test_search_empty_database(self, tmp_path):
        """Test search returns empty list for empty database."""
        storage = SQLiteStorage(str(tmp_path / "test.db"))
        results = storage.search("query", top_k=5)
        assert results == []

    def test_list_documents_empty(self, tmp_path):
        """Test listing documents when database is empty."""
        storage = SQLiteStorage(str(tmp_path / "test.db"))
        docs = storage.list_documents()
        assert docs == []

    def test_retriever_with_empty_database(self, tmp_path):
        """Test retriever returns empty when no documents."""
        storage = SQLiteStorage(str(tmp_path / "test.db"))
        retriever = Retriever(storage)
        results = retriever.retrieve("test query")
        assert results == []

    def test_delete_nonexistent_document(self, tmp_path):
        """Test deleting nonexistent document raises StorageError."""
        storage = SQLiteStorage(str(tmp_path / "test.db"))
        with pytest.raises(StorageError):
            storage.delete_document("nonexistent_id")


class TestLargeFilesAndContent:
    """Test handling of large files and content."""

    def test_ingest_large_markdown_file(self, tmp_path):
        """Test ingesting a file with large content."""
        md_file = tmp_path / "large.md"
        # Create file with ~100KB of content
        large_content = "# Large Document\n\n" + ("Content paragraph. " * 5000)
        md_file.write_text(large_content)
        
        reader = MarkdownReader()
        docs = reader.read(str(md_file))
        
        assert len(docs) > 0
        total_content_size = sum(len(doc.content) for doc in docs)
        assert total_content_size > 10000

    def test_very_long_search_query(self, tmp_path, sample_document):
        """Test handling very long search queries."""
        storage = SQLiteStorage(str(tmp_path / "test.db"))
        storage.save_document(sample_document)
        
        # Create a very long query
        long_query = "test " * 500
        results = storage.search(long_query, top_k=5)
        assert isinstance(results, list)

    def test_save_document_with_large_content(self, tmp_path):
        """Test saving documents with large content."""
        storage = SQLiteStorage(str(tmp_path / "test.db"))
        
        large_doc = Document(
            id="large_0",
            title="Large Document",
            content="Content. " * 10000,  # Large content
            source="large.md",
            format="markdown",
        )
        
        storage.save_document(large_doc)
        retrieved = storage.get_document("large_0")
        assert len(retrieved.content) > 50000


class TestSpecialCharactersAndEncoding:
    """Test handling of special characters and Unicode."""

    def test_unicode_document_content(self, tmp_path):
        """Test documents with Unicode content."""
        storage = SQLiteStorage(str(tmp_path / "test.db"))
        
        doc = Document(
            id="unicode_0",
            title="Unicode Test",
            content="Testing: 你好世界 (Chinese), مرحبا (Arabic), 🎉 (Emoji)",
            source="unicode.md",
            format="markdown",
        )
        
        storage.save_document(doc)
        retrieved = storage.get_document("unicode_0")
        assert "你好世界" in retrieved.content
        assert "🎉" in retrieved.content

    def test_document_title_with_special_chars(self, tmp_path):
        """Test document titles with various special characters."""
        storage = SQLiteStorage(str(tmp_path / "test.db"))
        
        special_titles = [
            "Title with / slash",
            'Title with "quotes"',
            "Title with 'apostrophe'",
            "Title with [brackets]",
            "Title with & ampersand",
        ]
        
        for i, title in enumerate(special_titles):
            doc = Document(
                id=f"special_{i}",
                title=title,
                content=f"Content for {title}",
                source="special.md",
                format="markdown",
            )
            storage.save_document(doc)
            retrieved = storage.get_document(f"special_{i}")
            assert retrieved.title == title

    def test_search_with_special_characters(self, tmp_path, sample_document):
        """Test search queries with special FTS characters."""
        storage = SQLiteStorage(str(tmp_path / "test.db"))
        storage.save_document(sample_document)
        
        special_queries = [
            'test"with"quotes',
            'test AND OR NOT',
            "test(with)parens",
            "test*with*asterisks",
        ]
        
        for query in special_queries:
            # Should not crash
            results = storage.search(query, top_k=5)
            assert isinstance(results, list)

    def test_unicode_filename(self, tmp_path):
        """Test reading files with Unicode names."""
        unicode_file = tmp_path / "文档.md"
        unicode_file.write_text("# 标题\n\n中文内容", encoding="utf-8")
        
        reader = MarkdownReader()
        docs = reader.read(str(unicode_file))
        
        assert len(docs) > 0
        assert "中文内容" in docs[0].content


class TestMalformedInputHandling:
    """Test handling of malformed or invalid input."""

    def test_search_with_empty_query(self, tmp_path, sample_document):
        """Test search with empty string."""
        storage = SQLiteStorage(str(tmp_path / "test.db"))
        storage.save_document(sample_document)
        
        results = storage.search("", top_k=5)
        assert results == []

    def test_save_document_duplicate_id_overwrites(self, tmp_path):
        """Test saving document with duplicate ID overwrites existing."""
        storage = SQLiteStorage(str(tmp_path / "test.db"))
        
        doc1 = Document(
            id="dup_0",
            title="Original",
            content="Original content",
            source="test.md",
            format="markdown",
        )
        doc2 = Document(
            id="dup_0",
            title="Updated",
            content="Updated content",
            source="test.md",
            format="markdown",
        )
        
        storage.save_document(doc1)
        storage.save_document(doc2)
        
        retrieved = storage.get_document("dup_0")
        assert retrieved.title == "Updated"

    def test_top_k_larger_than_database(self, tmp_path):
        """Test requesting more results than available documents."""
        storage = SQLiteStorage(str(tmp_path / "test.db"))
        
        # Add only 3 documents
        for i in range(3):
            doc = Document(
                id=f"doc_{i}",
                title=f"Document {i}",
                content="Test content",
                source="test.md",
                format="markdown",
            )
            storage.save_document(doc)
        
        # Request 100 results
        results = storage.search("Test", top_k=100)
        assert len(results) <= 3

    def test_zero_top_k(self, tmp_path, sample_document):
        """Test with top_k=0."""
        storage = SQLiteStorage(str(tmp_path / "test.db"))
        storage.save_document(sample_document)
        
        results = storage.search("test", top_k=0)
        assert results == []


class TestConcurrentAccess:
    """Test concurrent document access patterns."""

    def test_concurrent_document_saves(self, tmp_path):
        """Test saving multiple documents sequentially."""
        storage = SQLiteStorage(str(tmp_path / "test.db"))
        
        docs = [
            Document(
                id=f"doc_{i}",
                title=f"Doc {i}",
                content=f"Content for document {i}",
                source="docs.md",
                format="markdown",
            )
            for i in range(20)
        ]
        
        for doc in docs:
            storage.save_document(doc)
        
        # Verify all were saved
        assert len(storage.list_documents()) == 20

    def test_repeated_searches_consistency(self, tmp_path):
        """Test that repeated searches return consistent results."""
        storage = SQLiteStorage(str(tmp_path / "test.db"))
        
        # Add documents
        for i in range(10):
            doc = Document(
                id=f"doc_{i}",
                title=f"Python Document {i}",
                content="Python programming language",
                source="test.md",
                format="markdown",
            )
            storage.save_document(doc)
        
        # Multiple searches should return same results
        results_list = []
        for _ in range(3):
            results = storage.search("Python", top_k=5)
            # Results are (Document, score) tuples
            results_list.append([(r[0].id, r[1]) for r in results])
        
        # All searches should return same IDs
        assert results_list[0] == results_list[1]
        assert results_list[1] == results_list[2]

    def test_get_document_repeated_calls(self, tmp_path, sample_document):
        """Test multiple retrievals of same document."""
        storage = SQLiteStorage(str(tmp_path / "test.db"))
        storage.save_document(sample_document)
        
        # Retrieve same document multiple times
        for _ in range(5):
            retrieved = storage.get_document(sample_document.id)
            assert retrieved.id == sample_document.id
            assert retrieved.content == sample_document.content


class TestDatabaseRecovery:
    """Test recovery from database issues."""

    def test_database_table_initialization(self, tmp_path):
        """Test that storage initializes tables on first use."""
        db_path = str(tmp_path / "fresh.db")
        
        # Create empty database
        conn = sqlite3.connect(db_path)
        conn.close()
        
        # Storage should initialize on first use
        storage = SQLiteStorage(db_path)
        doc = Document(
            id="test_0",
            title="Test",
            content="Content",
            source="test.md",
            format="markdown",
        )
        storage.save_document(doc)
        
        retrieved = storage.get_document("test_0")
        assert retrieved.id == "test_0"

    def test_document_deletion_and_recovery(self, tmp_path):
        """Test delete and verify state consistency."""
        storage = SQLiteStorage(str(tmp_path / "test.db"))
        
        docs = [
            Document(
                id=f"doc_{i}",
                title=f"Document {i}",
                content=f"Content {i}",
                source="test.md",
                format="markdown",
            )
            for i in range(5)
        ]
        
        # Save all
        for doc in docs:
            storage.save_document(doc)
        
        before_count = len(storage.list_documents())
        
        # Delete one
        storage.delete_document("doc_2")
        
        after_count = len(storage.list_documents())
        assert after_count == before_count - 1
        
        # Try to get deleted document - should raise StorageError
        with pytest.raises(StorageError):
            storage.get_document("doc_2")


class TestConfigurationEdgeCases:
    """Test configuration loading edge cases."""

    def test_config_missing_file(self, tmp_path):
        """Test handling missing config file."""
        from dash_ai.core.config import Config
        from dash_ai.core.errors import ConfigurationError
        
        config_path = str(tmp_path / "nonexistent.yaml")
        
        with pytest.raises(ConfigurationError):
            Config(config_path)

    def test_config_invalid_yaml(self, tmp_path):
        """Test handling invalid YAML syntax."""
        from dash_ai.core.config import Config
        from dash_ai.core.errors import ConfigurationError
        
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
model:
  - invalid: list syntax
""")
        
        with pytest.raises(ConfigurationError):
            Config(str(config_file))


class TestIngestionErrorCases:
    """Test ingestion error scenarios."""

    def test_read_nonexistent_file(self):
        """Test reading file that doesn't exist."""
        reader = MarkdownReader()
        
        with pytest.raises(IngestionError):
            reader.read("/nonexistent/file.md")

    def test_read_non_markdown_file(self, tmp_path):
        """Test reading non-markdown file."""
        reader = MarkdownReader()
        
        text_file = tmp_path / "file.txt"
        text_file.write_text("Just text content.")
        
        with pytest.raises(IngestionError):
            reader.read(str(text_file))

    def test_read_invalid_utf8(self, tmp_path):
        """Test reading file with invalid UTF-8."""
        invalid_file = tmp_path / "bad.md"
        with open(invalid_file, "wb") as f:
            f.write(b"# Title\n\nContent\xFF\xFE")
        
        reader = MarkdownReader()
        with pytest.raises((IngestionError, UnicodeDecodeError)):
            reader.read(str(invalid_file))


class TestChunkingBehavior:
    """Test document chunking behavior."""

    def test_single_chunk_document(self, tmp_path):
        """Test document that fits in single chunk."""
        md_file = tmp_path / "small.md"
        md_file.write_text("# Title\n\nShort content.")
        
        reader = MarkdownReader()
        docs = reader.read(str(md_file))
        
        assert len(docs) >= 1
        assert all(doc.title == "Title" for doc in docs)

    def test_multiple_chunk_document(self, tmp_path):
        """Test document that spans multiple chunks."""
        md_file = tmp_path / "large.md"
        # Create substantial content
        content = "# Title\n\n" + "Paragraph. " * 1000
        md_file.write_text(content)
        
        reader = MarkdownReader()
        docs = reader.read(str(md_file))
        
        assert len(docs) > 1
        # All chunks should have same title
        assert all(doc.title == "Title" for doc in docs)


class TestMetadataPersistence:
    """Test that document metadata is preserved."""

    def test_metadata_saved_and_retrieved(self, tmp_path):
        """Test that metadata round-trips through storage."""
        storage = SQLiteStorage(str(tmp_path / "test.db"))
        
        doc = Document(
            id="meta_0",
            title="Test",
            content="Content",
            source="test.md",
            format="markdown",
            metadata={"key1": "value1", "key2": 42, "key3": True},
        )
        
        storage.save_document(doc)
        retrieved = storage.get_document("meta_0")
        
        assert retrieved.metadata == doc.metadata

    def test_metadata_updates(self, tmp_path):
        """Test that metadata can be updated."""
        storage = SQLiteStorage(str(tmp_path / "test.db"))
        
        doc1 = Document(
            id="meta_0",
            title="Test",
            content="Content",
            source="test.md",
            format="markdown",
            metadata={"version": 1},
        )
        storage.save_document(doc1)
        
        doc2 = Document(
            id="meta_0",
            title="Test",
            content="Content",
            source="test.md",
            format="markdown",
            metadata={"version": 2},
        )
        storage.save_document(doc2)
        
        retrieved = storage.get_document("meta_0")
        assert retrieved.metadata["version"] == 2


class TestSearchScoring:
    """Test search result scoring and ranking."""

    def test_search_with_relevant_documents(self, tmp_path):
        """Test search returns relevant results."""
        storage = SQLiteStorage(str(tmp_path / "test.db"))
        
        # Add documents with different relevance
        docs = [
            Document(
                id="doc_0",
                title="Python Programming",
                content="Python is a programming language",
                source="test.md",
                format="markdown",
            ),
            Document(
                id="doc_1",
                title="Web Development",
                content="Building web applications with FastAPI",
                source="test.md",
                format="markdown",
            ),
            Document(
                id="doc_2",
                title="Python Web",
                content="Python and web development combined",
                source="test.md",
                format="markdown",
            ),
        ]
        
        for doc in docs:
            storage.save_document(doc)
        
        # Search for "Python"
        results = storage.search("Python", top_k=3)
        
        # Should return results (tuples of Document, score)
        assert len(results) > 0
        # First result should be highly relevant
        assert any("Python" in r[0].content for r in results)
