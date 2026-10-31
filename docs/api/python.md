# Python API Reference

Use dash-ai as a Python library in your own applications.

## Installation

```bash
uv add --git https://github.com/edgar-treischl/dash-ai.git
# or
pip install git+https://github.com/edgar-treischl/dash-ai.git
```

## Quick Example

```python
from dash_ai.core.config import Config
from dash_ai.app import App

# Load configuration
config = Config.load_with_env()

# Initialize app
app = App(config)

# Ingest documents
app.ingest_files(["docs/guide.md", "docs/faq.md"])

# Ask a question
answer = app.ask_question("What is this project?")
print(answer)
```

## Core Classes

### `App`

Main application class for high-level operations.

**Location:** `dash_ai.app.App`

**Constructor:**
```python
App(config: Config)
```

**Methods:**

#### `ingest_files(file_paths: list[str]) -> None`
Ingest documents into the knowledge base.

```python
app.ingest_files(["docs/guide.md", "docs/api.md"])
```

**Arguments:**
- `file_paths` — List of file paths (supports glob patterns)

**Raises:**
- `FileNotFoundError` — If file doesn't exist
- `ValueError` — If file format not supported

---

#### `ask_question(question: str) -> str`
Ask a question and get an answer with sources.

```python
answer = app.ask_question("How do I configure Ollama?")
print(answer)
```

**Arguments:**
- `question` — User question (string)

**Returns:**
- Answer string with source attribution

**Raises:**
- `ValueError` — If no documents ingested
- `ConnectionError` — If Ollama unavailable

---

#### `list_documents() -> list[Document]`
Get all ingested documents.

```python
docs = app.list_documents()
for doc in docs:
    print(f"{doc.source}: {doc.title}")
```

**Returns:**
- List of Document objects

---

#### `delete_document(source: str) -> None`
Delete a document from knowledge base.

```python
app.delete_document("old-guide.md")
```

**Arguments:**
- `source` — Document source file name

**Raises:**
- `ValueError` — If document not found

---

### `Config`

Configuration management with YAML + environment variables.

**Location:** `dash_ai.core.config.Config`

**Class Methods:**

#### `load(path: str) -> Config`
Load configuration from YAML file.

```python
config = Config.load("config/settings.yaml")
```

---

#### `load_with_env() -> Config`
Load configuration with environment variable overrides.

```python
config = Config.load_with_env()
# OLLAMA_MODEL env var overrides config.model.model_name
```

**Environment Variables Supported:**
- `OLLAMA_HOST` — Ollama server URL
- `OLLAMA_MODEL` — Model name
- `OLLAMA_TIMEOUT` — Request timeout in seconds
- `DATABASE_PATH` — SQLite database path
- `RETRIEVAL_TOP_K` — Max documents to retrieve
- `RETRIEVAL_MIN_SCORE` — Minimum relevance score
- `APP_DEBUG` — Enable debug logging

---

### `Document`

Standardized document representation.

**Location:** `dash_ai.core.interfaces.Document`

**Attributes:**
```python
document = Document(
    id="doc_1_chunk_0",
    title="Introduction to Project",
    content="This is the document content...",
    source="guide.md",
    metadata={"chunk_index": 0, "page": 1}
)

print(document.id)        # "doc_1_chunk_0"
print(document.title)     # "Introduction to Project"
print(document.content)   # "This is the document content..."
print(document.source)    # "guide.md"
print(document.metadata)  # {"chunk_index": 0, "page": 1}
```

---

## Component Classes

### `MarkdownReader`

Parse and chunk Markdown files.

**Location:** `dash_ai.ingestion.markdown.MarkdownReader`

**Methods:**

#### `read_file(path: str) -> list[Document]`
```python
from dash_ai.ingestion.markdown import MarkdownReader

reader = MarkdownReader()
docs = reader.read_file("guide.md")

for doc in docs:
    print(f"{doc.source}: {doc.id}")
```

---

### `SQLiteStorage`

Persist documents and provide search.

**Location:** `dash_ai.knowledge.storage.SQLiteStorage`

**Constructor:**
```python
from dash_ai.knowledge.storage import SQLiteStorage

storage = SQLiteStorage("data/knowledge.db")
```

**Methods:**

#### `save_document(doc: Document) -> None`
```python
doc = Document(id="1", title="Test", content="...", source="test.md")
storage.save_document(doc)
```

---

#### `get_document(doc_id: str) -> Document`
```python
doc = storage.get_document("doc_1_chunk_0")
print(doc.title)
```

**Raises:** `ValueError` if document not found

---

#### `list_documents() -> list[Document]`
```python
all_docs = storage.list_documents()
```

---

#### `delete_document(doc_id: str) -> None`
```python
storage.delete_document("doc_1_chunk_0")
```

---

#### `search(query: str, top_k: int = 5, min_score: float = 0.1) -> list[tuple[Document, float]]`
Full-text search with scoring.

```python
results = storage.search("Python tutorial", top_k=10, min_score=0.2)

for doc, score in results:
    print(f"{doc.source}: {score:.2f}")
```

**Arguments:**
- `query` — Search query (string)
- `top_k` — Maximum results (default: 5)
- `min_score` — Minimum relevance score 0.0-1.0 (default: 0.1)

**Returns:**
- List of tuples: (Document, relevance_score)

---

### `OllamaModel`

Interface with local Ollama language model.

**Location:** `dash_ai.models.ollama.OllamaModel`

**Constructor:**
```python
from dash_ai.models.ollama import OllamaModel
from dash_ai.core.config import Config

config = Config.load_with_env()
model = OllamaModel(config.model)
```

**Methods:**

#### `generate(prompt: str) -> str`
Generate response from Ollama.

```python
response = model.generate("Tell me about Python")
print(response)
```

**Features:**
- Automatic retry with exponential backoff
- Connection verification
- Error handling with user-friendly messages

**Raises:**
- `ConnectionError` — Ollama not running or unreachable
- `TimeoutError` — Request timeout
- `ValueError` — Model not found

---

### `Retriever`

Document retrieval engine.

**Location:** `dash_ai.answering.retrieval.Retriever`

**Constructor:**
```python
from dash_ai.answering.retrieval import Retriever

retriever = Retriever(storage, config.retrieval)
```

**Methods:**

#### `retrieve(query: str, top_k: int = 5) -> list[tuple[Document, float]]`
```python
results = retriever.retrieve("How to install?", top_k=5)

for doc, score in results:
    print(f"{doc.source}: {score:.2f}")
```

---

### `AnsweringEngine`

RAG pipeline combining retrieval and generation.

**Location:** `dash_ai.answering.engine.AnsweringEngine`

**Constructor:**
```python
from dash_ai.answering.engine import AnsweringEngine

engine = AnsweringEngine(retriever, model)
```

**Methods:**

#### `answer(question: str) -> str`
Generate answer with source attribution.

```python
response = engine.answer("What is dash-ai?")
print(response)
# Output includes answer + sources
```

---

## Abstract Interfaces

Implement these to extend dash-ai.

### `ModelInterface`

**Location:** `dash_ai.core.interfaces.ModelInterface`

Implement to add new LLM providers:

```python
from dash_ai.core.interfaces import ModelInterface

class MyModel(ModelInterface):
    def __init__(self, config):
        self.config = config
    
    def generate(self, prompt: str) -> str:
        """Generate response from prompt."""
        # Your implementation
        return "response"
```

---

### `ReaderInterface`

**Location:** `dash_ai.core.interfaces.ReaderInterface`

Implement to add new input formats:

```python
from dash_ai.core.interfaces import ReaderInterface, Document

class PDFReader(ReaderInterface):
    def read_file(self, path: str) -> list[Document]:
        """Read and chunk PDF file."""
        documents = []
        # Your PDF parsing logic
        return documents
```

---

### `StorageInterface`

**Location:** `dash_ai.core.interfaces.StorageInterface`

Implement to add new storage backends:

```python
from dash_ai.core.interfaces import StorageInterface, Document

class PostgresStorage(StorageInterface):
    def save_document(self, doc: Document) -> None:
        pass
    
    def get_document(self, doc_id: str) -> Document:
        pass
    
    def list_documents(self) -> list[Document]:
        pass
    
    def delete_document(self, doc_id: str) -> None:
        pass
    
    def search(self, query: str, top_k: int, min_score: float) -> list[tuple[Document, float]]:
        pass
```

---

### `RetrievalInterface`

**Location:** `dash_ai.core.interfaces.RetrievalInterface`

Implement to add new search strategies:

```python
from dash_ai.core.interfaces import RetrievalInterface, Document

class VectorRetriever(RetrievalInterface):
    def retrieve(self, query: str, top_k: int) -> list[tuple[Document, float]]:
        """Retrieve documents using vector similarity."""
        pass
```

---

## Common Workflows

### Load Configuration from File

```python
from dash_ai.core.config import Config

config = Config.load("config/settings.yaml")
print(config.model.model_name)
print(config.storage.path)
```

### Load Configuration with Environment Overrides

```python
from dash_ai.core.config import Config
import os

os.environ["OLLAMA_MODEL"] = "neural-chat"
config = Config.load_with_env()
print(config.model.model_name)  # "neural-chat"
```

### Ingest Documents Programmatically

```python
from dash_ai.app import App
from dash_ai.core.config import Config

config = Config.load_with_env()
app = App(config)

# Ingest from list
files = ["doc1.md", "doc2.md", "doc3.md"]
app.ingest_files(files)

# Ingest with glob
import glob
files = glob.glob("docs/**/*.md", recursive=True)
app.ingest_files(files)
```

### Custom Search with Configuration

```python
from dash_ai.core.config import Config
from dash_ai.knowledge.storage import SQLiteStorage

config = Config.load_with_env()
storage = SQLiteStorage(config.storage.path)

# Search with custom parameters
results = storage.search(
    "Python programming",
    top_k=10,
    min_score=0.3
)

for doc, score in results:
    print(f"{doc.source} ({score:.0%}): {doc.content[:100]}")
```

### Build Custom Answer Pipeline

```python
from dash_ai.core.config import Config
from dash_ai.knowledge.storage import SQLiteStorage
from dash_ai.models.ollama import OllamaModel
from dash_ai.answering.retrieval import Retriever
from dash_ai.answering.engine import AnsweringEngine

config = Config.load_with_env()

# Initialize components
storage = SQLiteStorage(config.storage.path)
model = OllamaModel(config.model)
retriever = Retriever(storage, config.retrieval)
engine = AnsweringEngine(retriever, model)

# Ask question
answer = engine.answer("Your question here")
print(answer)
```

### Custom Ingest with Chunking

```python
from dash_ai.ingestion.markdown import MarkdownReader
from dash_ai.knowledge.storage import SQLiteStorage

reader = MarkdownReader()
storage = SQLiteStorage("data/custom.db")

# Read and parse
documents = reader.read_file("long-doc.md")
print(f"Created {len(documents)} chunks")

# Save each chunk
for doc in documents:
    storage.save_document(doc)
    print(f"Saved: {doc.id}")
```

---

## Error Handling

### Connection Errors

```python
from dash_ai.models.ollama import OllamaModel
from dash_ai.core.config import Config

try:
    config = Config.load_with_env()
    model = OllamaModel(config.model)
except ConnectionError as e:
    print(f"Cannot connect to Ollama: {e}")
    print("Start Ollama with: ollama serve")
```

### Missing Documents

```python
from dash_ai.app import App
from dash_ai.core.config import Config

try:
    config = Config.load_with_env()
    app = App(config)
    answer = app.ask_question("question")
except ValueError as e:
    print(f"No documents ingested: {e}")
    print("Ingest first with: app.ingest_files(['doc.md'])")
```

### File Errors

```python
from dash_ai.app import App
from dash_ai.core.config import Config

try:
    config = Config.load_with_env()
    app = App(config)
    app.ingest_files(["missing.md"])
except FileNotFoundError as e:
    print(f"File not found: {e}")
    print("Check path and try again")
```

---

## Performance Tips

- **Batch operations** — Ingest multiple files at once
- **Reuse connections** — Keep storage/model objects alive
- **Tune parameters** — Adjust `top_k`, `min_score`, `timeout`
- **Index optimization** — Let FTS5 build index (takes time on first run)
- **Monitor queries** — Enable `APP_DEBUG=true` for insights

---

## Further Reading

- [Architecture Overview](../architecture/overview.md)
- [Configuration Guide](../guides/configuration.md)
- [CLI Reference](cli.md)
- [Contributing Guide](../contributing/guide.md)

