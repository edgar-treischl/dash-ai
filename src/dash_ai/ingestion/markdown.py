"""Markdown file reader and ingestion."""

from pathlib import Path
from typing import List

from dash_ai.core.errors import IngestionError
from dash_ai.core.interfaces import Document, ReaderInterface


class MarkdownReader(ReaderInterface):
    """Read Markdown files and convert to Document chunks."""

    TARGET_CHUNK_SIZE = 500

    def supports_format(self, file_path: str) -> bool:
        """Check if file is Markdown.

        Args:
            file_path: Path to file

        Returns:
            True if file ends with .md or .markdown
        """
        return file_path.lower().endswith((".md", ".markdown"))

    def read(self, file_path: str) -> List[Document]:
        """Read Markdown file and return Document chunks.

        Args:
            file_path: Path to Markdown file

        Returns:
            List of Document objects, one per chunk

        Raises:
            IngestionError: If file not found, not Markdown, or read fails
        """
        path = Path(file_path)
        if not path.exists():
            raise IngestionError(
                f"File not found: {file_path}",
                suggestion="Check the file path is correct",
            )

        if not self.supports_format(file_path):
            raise IngestionError(
                f"Not a Markdown file: {file_path}",
                suggestion="Only .md and .markdown files are supported",
            )

        try:
            # Read file content
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError as e:
            raise IngestionError(
                f"Failed to read file (encoding error): {file_path}",
                suggestion="Make sure file is UTF-8 encoded",
            ) from e
        except OSError as e:
            raise IngestionError(
                f"Failed to read file: {e}",
                suggestion="Check file permissions",
            ) from e

        # Extract title (first H1 or filename)
        title = self._extract_title(content, path.stem)

        # Split into chunks
        chunks = self._chunk_content(content)

        # Create Document objects
        documents = []
        for idx, chunk in enumerate(chunks):
            doc_id = f"{path.stem}_{idx}"
            doc = Document(
                id=doc_id,
                title=title,
                content=chunk,
                source=str(path),
                format="markdown",
                metadata={
                    "chunk_index": idx,
                    "total_chunks": len(chunks),
                    "filename": path.name,
                },
            )
            documents.append(doc)

        return documents

    def _extract_title(self, content: str, default: str) -> str:
        """Extract title from content or use default.

        Args:
            content: File content
            default: Default title if not found in content

        Returns:
            Title string
        """
        lines = content.split("\n")
        for line in lines:
            if line.startswith("# "):
                return line[2:].strip()
        return default

    def _chunk_content(self, content: str) -> List[str]:
        """Split content into chunks by paragraphs.

        Uses paragraph-based strategy: split by double newlines,
        combine until reaching target size.

        Args:
            content: File content to chunk

        Returns:
            List of content chunks
        """
        paragraphs = content.split("\n\n")
        chunks = []
        current_chunk = []
        current_size = 0

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            para_size = len(para)

            # If adding this paragraph exceeds target and we have content, start new chunk
            if current_size + para_size > self.TARGET_CHUNK_SIZE and current_chunk:
                chunks.append("\n\n".join(current_chunk))
                current_chunk = [para]
                current_size = para_size
            else:
                current_chunk.append(para)
                current_size += para_size + 2  # +2 for \n\n separator

        # Add remaining content
        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        return chunks if chunks else [""]
