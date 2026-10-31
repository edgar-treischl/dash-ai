# User Guide

Complete guide to installing, configuring, and using Dash-AI.

---

## Table of Contents

1. [Installation](#installation)
2. [Quick Start (5 minutes)](#quick-start-5-minutes)
3. [CLI Commands](#cli-commands)
4. [Interactive Mode](#interactive-mode)
5. [Configuration](#configuration)
6. [JSON Output](#json-output)
7. [Advanced Usage](#advanced-usage)
8. [Troubleshooting](#troubleshooting)

---

## Installation

### Prerequisites

- **Python 3.10+** — [Install here](https://www.python.org/downloads/)
- **Ollama** — [Download here](https://ollama.ai)
- **Git** (for cloning the repository)

### Step 1: Install Python & Ollama

**macOS:**
```bash
# Python: Use Homebrew or download from python.org
brew install python@3.11

# Ollama: Download app or
brew install ollama
```

**Linux (Ubuntu/Debian):**
```bash
# Python
sudo apt-get update
sudo apt-get install python3.11 python3.11-venv

# Ollama
curl https://ollama.ai/install.sh | sh
```

**Windows:**
- Use WSL2 (recommended): [Install WSL2](https://docs.microsoft.com/windows/wsl/install)
- Then follow Linux steps

### Step 2: Clone and Install Dash-AI

```bash
# Clone the repository
git clone https://github.com/edgar-treischl/dash-ai.git
cd dash-ai

# Install dependencies with uv (fast, recommended)
# If you don't have uv, install it: curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync

# OR use pip
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 3: Start Ollama

```bash
# Start the Ollama service
ollama serve

# In another terminal, download a model
ollama pull llama2  # Default model

# Verify it works
curl http://localhost:11434/api/tags
```

### Step 4: Verify Installation

```bash
# Check Dash-AI is installed
dash-ai --version

# Try your first question
dash-ai ask "Hello, what is your name?"
# Should respond with something like: "I'm Llama 2, an AI assistant..."
```

**That's it! You're ready to use Dash-AI.**

---

## Quick Start (5 minutes)

### 1. Create a Knowledge Base

Create a directory with Markdown files:

```bash
# Create directory
mkdir -p data/knowledge

# Create a sample markdown file
cat > data/knowledge/sample.md << 'EOF'
# Python Basics

Python is a high-level, interpreted programming language.

## Variables

Variables are containers for storing data values.

```python
name = "Alice"
age = 30
price = 19.99
```

## Functions

Functions are reusable blocks of code.

```python
def greet(name):
    return f"Hello, {name}!"
```

## Lists

Lists are ordered, changeable collections.

```python
fruits = ["apple", "banana", "cherry"]
```
EOF

# Verify the file was created
cat data/knowledge/sample.md
```

### 2. Ingest Documents

```bash
# Add documents to Dash-AI
dash-ai ingest data/knowledge/

# Output:
# ✓ Imported 1 file
# ✓ Created 8 chunks
# Knowledge base ready!
```

### 3. Ask Questions

```bash
# Ask your first question
dash-ai ask "What is Python?"

# Output:
# Answer:
# Python is a high-level, interpreted programming language...
#
# Sources:
# - data/knowledge/sample.md (relevance: 0.95)
```

### 4. View Your Knowledge Base

```bash
# List all documents
dash-ai list

# Output:
# Documents in knowledge base:
# 1. sample.md (8 chunks, added Oct 31 14:45)
# Total: 1 document, 8 chunks
```

### 5. Interactive Conversation (Optional)

```bash
# Start interactive mode
dash-ai chat

# Output:
# Starting interactive session...
# Type 'exit' to quit.
# 
# > Ask a question: What are Python variables?
# Answer: Variables are containers for storing data values...
#
# > Ask a question: Show me an example
# Answer: Sure! Here's a simple example...
#
# > Ask a question: exit
# Session ended. 2 questions in 3.2s
```

**Congratulations!** You've successfully used Dash-AI. Now explore more advanced features.

---

## CLI Commands

### `ingest` — Add Documents

```bash
# Ingest a single file
dash-ai ingest document.md

# Ingest an entire directory
dash-ai ingest data/knowledge/

# Ingest multiple locations
dash-ai ingest docs/ data/guides/ notes.md

# See what would be ingested without actually doing it
dash-ai ingest data/knowledge/ --dry-run

# Show detailed output
dash-ai ingest data/knowledge/ --verbose
```

**Options:**
- `--dry-run` — Preview without ingesting
- `--verbose` — Show detailed progress
- `--json` — Output in JSON format

**Examples:**
```bash
# Add company handbook
dash-ai ingest company_handbook.md

# Add multiple documentation folders
dash-ai ingest docs/ help/ faq.md

# Check what will be added
dash-ai ingest large_directory/ --dry-run --verbose
```

### `ask` — Ask Questions

```bash
# Simple question
dash-ai ask "What is machine learning?"

# Complex question with multiple terms
dash-ai ask "How do I implement a neural network in Python?"

# Get JSON output for automation
dash-ai ask "What are the main components?" --json

# Show verbose output (includes timing and sources)
dash-ai ask "Your question" --verbose

# Limit to specific number of sources
dash-ai ask "question" --sources 5
```

**Options:**
- `--json` — Output in JSON format
- `--verbose` — Show search results and timing
- `--sources N` — Limit to N source documents (default: 3)

**Output example:**
```
Question: What is Python?

Answer:
Python is a high-level, interpreted programming language known for its
simplicity and readability. It is widely used for web development, data
science, and automation.

Sources:
- data/knowledge/python-basics.md (Relevance: 0.92)
  "Python is a high-level, interpreted programming language..."
- data/knowledge/tutorial.md (Relevance: 0.87)
  "Python is easy to learn because of its simple syntax..."

Generated in 2.34s
Search took 0.05s
```

### `chat` — Interactive Mode

```bash
# Start interactive session
dash-ai chat

# You'll see:
# Starting interactive session...
# Type 'exit' or 'quit' to end. Type 'help' for commands.
# 
# > Ask a question: [waiting for input]
```

**Interactive commands:**
- Type a question → Get an answer
- `help` → Show available commands
- `exit` or `quit` → End session
- `clear` → Clear screen
- `reset` → Clear conversation history
- `Ctrl+D` → End session (Unix-like systems)

**Interactive features:**
- Multi-turn conversation (history maintained)
- Numbered questions in session
- Session timing and statistics
- Graceful error handling

### `list` — View Documents

```bash
# List all documents
dash-ai list

# Get JSON output
dash-ai list --json

# Show detailed information
dash-ai list --verbose
```

**Output example:**
```
Documents in knowledge base:
1. python-basics.md (5 chunks, added Oct 31 14:20)
2. web-development.md (12 chunks, added Oct 31 14:25)
3. data-science.md (8 chunks, added Oct 31 14:30)

Total: 3 documents
Total chunks: 25
Database size: 2.3 MB
```

### `delete` — Remove Documents

```bash
# Delete a specific document
dash-ai delete python-basics.md

# Delete all documents
dash-ai delete --all

# Confirm before deleting
dash-ai delete python-basics.md --confirm
```

**Warning:** Deletion is permanent. Backup important data first.

---

## Interactive Mode

### Starting a Session

```bash
$ dash-ai chat
Starting interactive session...
Type 'exit' to quit. Type 'help' for commands.
```

### Example Session

```
> What is machine learning?
Thinking...

Answer: Machine learning is a subset of artificial intelligence...
Sources: python-basics.md

> Tell me more about supervised learning
Thinking...

Answer: Supervised learning is a type of machine learning where...
Sources: python-basics.md, data-science.md

> What are examples?
Thinking...

Answer: Common examples include classification and regression...
Sources: data-science.md

> exit
Session complete. Asked 3 questions in 8.5s.
```

### Advanced Interactive Features

**Multi-turn context:**
- Dash-AI maintains conversation history
- Follow-up questions reference previous answers
- Natural conversation flow

**Session summary:**
```
Session Statistics:
- Questions asked: 5
- Total response time: 12.3s
- Average time per question: 2.46s
- Documents referenced: 3
```

**Keyboard shortcuts:**
- `Ctrl+C` — Exit (gracefully closes session)
- `Ctrl+D` — End input (Unix-like systems)

---

## Configuration

### Configuration File

Create `config/settings.yaml`:

```yaml
# Model settings
model:
  name: llama2              # Model name from Ollama
  max_tokens: 512          # Max tokens in response
  temperature: 0.7         # Randomness (0=deterministic, 1=random)

# Ollama connection
ollama:
  base_url: http://localhost:11434
  timeout: 30              # Seconds

# Storage
storage:
  database_path: ~/.local/share/dash-ai/db.sqlite
  chunk_size: 512          # Characters per chunk

# Logging
logging:
  level: INFO              # DEBUG, INFO, WARNING, ERROR
  file: ~/.local/share/dash-ai/app.log
```

### Environment Variables

Override settings without editing config:

```bash
# Model
MODEL_NAME=mistral dash-ai ask "question"
MODEL_MAX_TOKENS=256 dash-ai ask "question"

# Ollama
OLLAMA_BASE_URL=http://custom-host:11434 dash-ai ask "question"

# Storage
DASH_AI_DATA_DIR=/custom/path dash-ai ask "question"

# Logging
LOG_LEVEL=DEBUG dash-ai ask "question"
```

### Setting Custom Models

```bash
# Download alternative model
ollama pull mistral
ollama pull neural-chat
ollama pull orca-mini

# Check available models
ollama list

# Use different model
MODEL_NAME=mistral dash-ai ask "Quick question"
```

**Popular models:**

| Model | Speed | Quality | Memory | Best For |
|-------|-------|---------|--------|----------|
| mistral | ⚡⚡ | Good | 5GB | Fast responses |
| llama2 | ⚡ | Excellent | 4GB | Balanced (default) |
| neural-chat | ⚡⚡ | Good | 5GB | Conversations |
| orca-mini | ⚡⚡⚡ | Fair | 2GB | Low-resource |

---

## JSON Output

### Using `--json` Flag

```bash
# Get JSON output
dash-ai ask "What is Python?" --json

# Parse with jq (Linux/macOS)
dash-ai ask "What is Python?" --json | jq '.answer'
```

### JSON Response Format

**Success response:**
```json
{
  "status": "success",
  "question": "What is Python?",
  "answer": "Python is a high-level, interpreted programming language...",
  "generation_time_ms": 2345,
  "search_time_ms": 45,
  "sources": [
    {
      "document_id": "python-basics.md-chunk-0",
      "source_file": "data/knowledge/python-basics.md",
      "relevance_score": 0.95,
      "excerpt": "Python is a high-level, interpreted..."
    }
  ]
}
```

**Error response:**
```json
{
  "status": "error",
  "error_type": "ModelError",
  "error_message": "Ollama connection refused",
  "suggestion": "Is Ollama running? Start with: ollama serve"
}
```

### Automating with JSON

```bash
#!/bin/bash
# Process multiple questions and extract answers

while read question; do
  echo "Q: $question"
  response=$(dash-ai ask "$question" --json)
  answer=$(echo "$response" | jq -r '.answer')
  echo "A: $answer"
  echo
done < questions.txt
```

---

## Advanced Usage

### Batch Processing

```bash
# Process multiple files
for file in data/knowledge/*.md; do
  dash-ai ingest "$file" --verbose
done

# Process multiple questions
cat questions.txt | while read question; do
  dash-ai ask "$question" --json
done
```

### Using as Python Library

```python
from dash_ai import App

# Initialize
app = App()

# Ask questions
result = app.ask("What is Python?")
print(result.text)
print(f"Time: {result.generation_time_ms}ms")

# Access sources
for source in result.sources:
    print(f"- {source.source_file}: {source.excerpt}")

# Add documents programmatically
app.ingest_document("path/to/file.md")

# Get all documents
documents = app.storage.get_all_documents()
```

### Custom Configuration

```python
from dash_ai import App, Config

# Use custom configuration
config = Config(
    model_name="mistral",
    ollama_base_url="http://localhost:11434",
    max_tokens=256
)

app = App(config=config)
result = app.ask("your question")
```

### Performance Monitoring

```bash
# Measure performance
time dash-ai ingest large_directory/

# Get detailed timing
dash-ai ask "question" --verbose

# Profile memory usage
/usr/bin/time -l dash-ai ask "question"  # macOS
/usr/bin/time -v dash-ai ask "question"  # Linux
```

---

## Troubleshooting

### Common Issues

**Issue: "Ollama connection refused"**
```bash
# Solution 1: Start Ollama
ollama serve

# Solution 2: Check if Ollama is running
curl http://localhost:11434/api/tags

# Solution 3: Custom URL
OLLAMA_BASE_URL=http://your-server:11434 dash-ai ask "question"
```

**Issue: "Model not found"**
```bash
# Download the model
ollama pull llama2

# Verify it's installed
ollama list
```

**Issue: "No documents found"**
```bash
# Check if documents were ingested
dash-ai list

# If empty, ingest them
dash-ai ingest data/knowledge/
```

**Issue: "Slow responses"**
```bash
# Try faster model
ollama pull mistral
MODEL_NAME=mistral dash-ai ask "question"

# Close other applications
# Check disk space: df -h
```

See [Troubleshooting Guide](troubleshooting.md) for more detailed help.

---

## Best Practices

### 1. Organize Documents

```
data/knowledge/
├── architecture/
│   ├── overview.md
│   └── components.md
├── guides/
│   ├── getting-started.md
│   └── advanced-usage.md
└── reference/
    ├── api.md
    └── config.md
```

### 2. Ask Specific Questions

```bash
# ❌ Vague
dash-ai ask "Tell me about Python"

# ✅ Specific
dash-ai ask "How do I use list comprehensions in Python?"
```

### 3. Maintain Your Knowledge Base

```bash
# Regularly back up
cp ~/.local/share/dash-ai/db.sqlite ~/backups/db.$(date +%Y%m%d).sqlite

# Remove outdated documents
dash-ai list  # Find old documents
dash-ai delete outdated-doc.md
```

### 4. Optimize Performance

```bash
# Use faster model for quick responses
MODEL_NAME=mistral dash-ai ask "quick question"

# Use full model for complex questions
MODEL_NAME=llama2 dash-ai ask "complex question requiring deep reasoning"
```

---

## Getting Help

- 📖 Read [FAQ](faq.md) for common questions
- 🔧 Check [Troubleshooting Guide](troubleshooting.md) for issues
- 💡 See [Examples](examples.md) for usage ideas
- 🚀 Review [Architecture Guide](../user_guide/architecture/overview.md) for deep dives
- 💬 Ask in [GitHub Discussions](https://github.com/edgar-treischl/dash-ai/discussions)
- 🐛 Report bugs on [GitHub Issues](https://github.com/edgar-treischl/dash-ai/issues)

---

**Last updated:** October 31, 2024  
**Applies to:** Phase 2+
