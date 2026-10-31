"""Performance regression and benchmark tests for dash-ai.

These tests measure key performance metrics to detect regressions
and ensure the system remains responsive.
"""

import time
from pathlib import Path

import pytest

from dash_ai.answering.retrieval import Retriever
from dash_ai.core.interfaces import Document
from dash_ai.ingestion.markdown import MarkdownReader
from dash_ai.knowledge.storage import SQLiteStorage


class TestIngestionPerformance:
    """Test ingestion speed and efficiency."""

    def test_single_file_ingestion_completes_quickly(self, tmp_path):
        """Test that ingesting a single file completes in reasonable time."""
        md_file = tmp_path / "test.md"
        # Create moderate-sized content
        content = "# Title\n\n" + ("Content paragraph. " * 200)
        md_file.write_text(content)
        
        reader = MarkdownReader()
        
        start = time.time()
        docs = reader.read(str(md_file))
        elapsed = time.time() - start
        
        # Should complete in < 1 second
        assert elapsed < 1.0
        assert len(docs) > 0

    def test_document_storage_throughput(self, tmp_path):
        """Test that storing documents has reasonable throughput."""
        storage = SQLiteStorage(str(tmp_path / "test.db"))
        
        docs = [
            Document(
                id=f"doc_{i}",
                title=f"Document {i}",
                content=f"Content {i}\n" * 5,
                source="test.md",
                format="markdown",
            )
            for i in range(50)
        ]
        
        start = time.time()
        for doc in docs:
            storage.save_document(doc)
        elapsed = time.time() - start
        
        # Should store 50 documents in < 2 seconds
        assert elapsed < 2.0

    def test_list_documents_performance(self, tmp_path):
        """Test that listing documents is fast."""
        storage = SQLiteStorage(str(tmp_path / "test.db"))
        
        # Create 100 documents
        for i in range(100):
            doc = Document(
                id=f"doc_{i}",
                title=f"Document {i}",
                content=f"Content {i}",
                source="test.md",
                format="markdown",
            )
            storage.save_document(doc)
        
        start = time.time()
        docs = storage.list_documents()
        elapsed = time.time() - start
        
        # Should list 100 documents in < 200ms
        assert elapsed < 0.2
        assert len(docs) == 100


class TestSearchPerformance:
    """Test search query performance."""

    def test_search_latency_small_database(self, tmp_path):
        """Test search latency with small document set."""
        storage = SQLiteStorage(str(tmp_path / "test.db"))
        
        # Add 10 documents
        for i in range(10):
            doc = Document(
                id=f"doc_{i}",
                title=f"Python {i}",
                content="Python is a programming language " * 20,
                source="test.md",
                format="markdown",
            )
            storage.save_document(doc)
        
        start = time.time()
        results = storage.search("Python", top_k=5)
        elapsed = time.time() - start
        
        # Should search in < 100ms
        assert elapsed < 0.1
        assert len(results) > 0

    def test_search_latency_medium_database(self, tmp_path):
        """Test search latency with moderate document set."""
        storage = SQLiteStorage(str(tmp_path / "test.db"))
        
        # Add 100 documents
        for i in range(100):
            doc = Document(
                id=f"doc_{i}",
                title=f"Document {i}",
                content=f"Content {i}" * 10,
                source="test.md",
                format="markdown",
            )
            storage.save_document(doc)
        
        start = time.time()
        results = storage.search("Content", top_k=5)
        elapsed = time.time() - start
        
        # Should search in < 200ms
        assert elapsed < 0.2
        assert len(results) > 0

    def test_retriever_performance(self, tmp_path):
        """Test retriever's retrieval speed."""
        storage = SQLiteStorage(str(tmp_path / "test.db"))
        retriever = Retriever(storage)
        
        # Add documents
        for i in range(50):
            doc = Document(
                id=f"doc_{i}",
                title=f"Python Programming {i}",
                content="Python programming language",
                source="test.md",
                format="markdown",
            )
            storage.save_document(doc)
        
        start = time.time()
        results = retriever.retrieve("Python")
        elapsed = time.time() - start
        
        # Should retrieve in < 200ms
        assert elapsed < 0.2
        assert len(results) > 0

    def test_search_consistency(self, tmp_path):
        """Test that repeated searches return consistent results."""
        storage = SQLiteStorage(str(tmp_path / "test.db"))
        
        # Add documents
        for i in range(20):
            doc = Document(
                id=f"doc_{i}",
                title=f"Test {i}",
                content="Test content",
                source="test.md",
                format="markdown",
            )
            storage.save_document(doc)
        
        # Multiple searches should return same results
        results_list = []
        for _ in range(3):
            results = storage.search("Test", top_k=5)
            # Results are (Document, score) tuples
            results_list.append([(r[0].id, r[1]) for r in results])
        
        # All should be identical
        assert results_list[0] == results_list[1]
        assert results_list[1] == results_list[2]


class TestRetrievalPerformance:
    """Test individual document retrieval performance."""

    def test_single_document_retrieval(self, tmp_path, sample_document):
        """Test that retrieving a single document is instant."""
        storage = SQLiteStorage(str(tmp_path / "test.db"))
        storage.save_document(sample_document)
        
        start = time.time()
        doc = storage.get_document(sample_document.id)
        elapsed = time.time() - start
        
        # Should be < 10ms
        assert elapsed < 0.01
        assert doc is not None

    def test_repeated_document_retrieval(self, tmp_path, sample_document):
        """Test that retrieving same document multiple times is fast."""
        storage = SQLiteStorage(str(tmp_path / "test.db"))
        storage.save_document(sample_document)
        
        start = time.time()
        for _ in range(100):
            storage.get_document(sample_document.id)
        elapsed = time.time() - start
        
        # 100 retrievals should be < 1 second
        assert elapsed < 1.0


class TestEndToEndPerformance:
    """Test complete workflows for performance."""

    def test_ingest_and_search_workflow(self, tmp_path):
        """Test complete ingest and search workflow."""
        # Create markdown file
        md_file = tmp_path / "doc.md"
        md_file.write_text("# Python\n\nPython is a language.\n" * 50)
        
        # Setup
        reader = MarkdownReader()
        storage = SQLiteStorage(str(tmp_path / "test.db"))
        
        # Measure complete workflow
        start = time.time()
        
        # Ingest
        docs = reader.read(str(md_file))
        for doc in docs:
            storage.save_document(doc)
        
        # Search
        results = storage.search("Python", top_k=5)
        
        total_time = time.time() - start
        
        # Total workflow should complete in < 2 seconds
        assert total_time < 2.0
        assert len(results) > 0

    def test_no_results_search_performance(self, tmp_path):
        """Test that searches with no results are still fast."""
        storage = SQLiteStorage(str(tmp_path / "test.db"))
        
        # Add some documents
        for i in range(30):
            doc = Document(
                id=f"doc_{i}",
                title=f"Python {i}",
                content="Python content",
                source="test.md",
                format="markdown",
            )
            storage.save_document(doc)
        
        start = time.time()
        results = storage.search("nonexistentword12345", top_k=5)
        elapsed = time.time() - start
        
        # Should still be fast
        assert elapsed < 0.2
        assert results == []


@pytest.mark.slow
class TestMemoryEfficiency:
    """Test memory usage during operations."""

    def test_large_document_storage(self, tmp_path):
        """Test storing documents with large content."""
        storage = SQLiteStorage(str(tmp_path / "test.db"))
        
        # Create large document
        large_content = "Content paragraph. " * 5000
        doc = Document(
            id="large_0",
            title="Large Document",
            content=large_content,
            source="large.md",
            format="markdown",
        )
        
        storage.save_document(doc)
        retrieved = storage.get_document("large_0")
        
        assert len(retrieved.content) > 50000

    def test_many_small_documents(self, tmp_path):
        """Test storing many small documents."""
        storage = SQLiteStorage(str(tmp_path / "test.db"))
        
        # Store 500 documents
        for i in range(500):
            doc = Document(
                id=f"doc_{i}",
                title=f"Document {i}",
                content=f"Content {i}",
                source="docs.md",
                format="markdown",
            )
            storage.save_document(doc)
        
        # Should be able to list them
        docs = storage.list_documents()
        assert len(docs) == 500


class TestSearchQualityMetrics:
    """Test quality of search results."""

    def test_top_k_parameter_respected(self, tmp_path):
        """Test that top_k parameter limits results correctly."""
        storage = SQLiteStorage(str(tmp_path / "test.db"))
        
        # Add 20 documents with matching content
        for i in range(20):
            doc = Document(
                id=f"doc_{i}",
                title=f"Test {i}",
                content="Test content matching",
                source="test.md",
                format="markdown",
            )
            storage.save_document(doc)
        
        # Search with different top_k values
        results_5 = storage.search("Test", top_k=5)
        results_10 = storage.search("Test", top_k=10)
        results_20 = storage.search("Test", top_k=20)
        
        assert len(results_5) <= 5
        assert len(results_10) <= 10
        assert len(results_20) <= 20

    def test_search_relevance_basic(self, tmp_path):
        """Test that search returns relevant results."""
        storage = SQLiteStorage(str(tmp_path / "test.db"))
        
        # Add documents with different content
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
                title="JavaScript Basics",
                content="JavaScript for web development",
                source="test.md",
                format="markdown",
            ),
        ]
        
        for doc in docs:
            storage.save_document(doc)
        
        # Search for Python
        results = storage.search("Python", top_k=2)
        
        # Should return results (tuples of Document, score)
        assert len(results) > 0
        # Python result should be included
        assert any("doc_0" == r[0].id for r in results)


class TestDatabaseOperationSpeed:
    """Test database operation performance."""

    def test_document_deletion_speed(self, tmp_path):
        """Test that deleting documents is fast."""
        storage = SQLiteStorage(str(tmp_path / "test.db"))
        
        # Add documents
        for i in range(50):
            doc = Document(
                id=f"doc_{i}",
                title=f"Document {i}",
                content=f"Content {i}",
                source="test.md",
                format="markdown",
            )
            storage.save_document(doc)
        
        start = time.time()
        for i in range(25):
            storage.delete_document(f"doc_{i}")
        elapsed = time.time() - start
        
        # Should delete 25 documents in < 1 second
        assert elapsed < 1.0

    def test_document_update_speed(self, tmp_path):
        """Test that updating documents is fast."""
        storage = SQLiteStorage(str(tmp_path / "test.db"))
        
        doc = Document(
            id="doc_0",
            title="Document",
            content="Original content",
            source="test.md",
            format="markdown",
        )
        storage.save_document(doc)
        
        start = time.time()
        for i in range(50):
            doc.content = f"Updated content {i}"
            storage.save_document(doc)
        elapsed = time.time() - start
        
        # Should update 50 times in < 1 second
        assert elapsed < 1.0
