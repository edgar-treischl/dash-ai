"""Tests for Markdown ingestion."""

import pytest

from dash_ai.ingestion.markdown import MarkdownReader


@pytest.fixture
def reader():
    """Create a MarkdownReader instance."""
    return MarkdownReader()


def test_supports_format(reader):
    """Test format detection."""
    assert reader.supports_format("test.md")
    assert reader.supports_format("document.markdown")
    assert not reader.supports_format("test.txt")
    assert not reader.supports_format("test.pdf")


def test_read_markdown_file(reader, tmp_path):
    """Test reading a Markdown file."""
    # Create test file
    md_file = tmp_path / "test.md"
    content = """# Test Document

This is the first paragraph with some content about testing.

This is the second paragraph with more information.

And here's a third paragraph for good measure."""

    with open(md_file, "w") as f:
        f.write(content)

    # Read file
    documents = reader.read(str(md_file))

    assert len(documents) > 0
    assert all(doc.format == "markdown" for doc in documents)
    assert all(doc.source == str(md_file) for doc in documents)
    assert documents[0].title == "Test Document"


def test_read_file_not_found(reader):
    """Test error when file not found."""
    with pytest.raises(FileNotFoundError):
        reader.read("nonexistent.md")


def test_read_non_markdown_file(reader, tmp_path):
    """Test error when file is not Markdown."""
    txt_file = tmp_path / "test.txt"
    txt_file.write_text("Not markdown")

    with pytest.raises(ValueError, match="Not a Markdown file"):
        reader.read(str(txt_file))


def test_chunk_content(reader):
    """Test paragraph-based chunking."""
    content = """First paragraph.

Second paragraph.

Third paragraph."""

    chunks = reader._chunk_content(content)

    assert len(chunks) > 0
    assert all(isinstance(chunk, str) for chunk in chunks)


def test_extract_title(reader):
    """Test title extraction from content."""
    # Test with H1
    content = "# My Title\n\nContent here"
    title = reader._extract_title(content, "default")
    assert title == "My Title"

    # Test with default
    content = "No heading here\n\nJust content"
    title = reader._extract_title(content, "default")
    assert title == "default"


def test_document_id_generation(reader, tmp_path):
    """Test unique document ID generation."""
    md_file = tmp_path / "docs.md"
    content = "Para 1\n\nPara 2\n\nPara 3"

    with open(md_file, "w") as f:
        f.write(content)

    documents = reader.read(str(md_file))

    # Check IDs are unique and formatted correctly
    ids = [doc.id for doc in documents]
    assert len(ids) == len(set(ids))  # All unique

    for doc in documents:
        assert doc.id.startswith("docs_")
        assert "_" in doc.id
        chunk_idx = int(doc.id.split("_")[-1])
        assert chunk_idx == doc.metadata["chunk_index"]


def test_document_metadata(reader, tmp_path):
    """Test metadata includes chunk information."""
    md_file = tmp_path / "test.md"
    with open(md_file, "w") as f:
        f.write("Content 1\n\nContent 2")

    documents = reader.read(str(md_file))

    for i, doc in enumerate(documents):
        assert "chunk_index" in doc.metadata
        assert "total_chunks" in doc.metadata
        assert doc.metadata["chunk_index"] == i
        assert doc.metadata["total_chunks"] == len(documents)
        assert "filename" in doc.metadata
