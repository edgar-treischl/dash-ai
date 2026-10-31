# Frequently Asked Questions (FAQ)

---

## General Questions

### What is Dash-AI?

Dash-AI is a **local-first AI knowledge assistant** that helps you ask questions about documents you provide. It uses a language model running on your machine (via Ollama) to generate answers based on your knowledge base.

**Key features:**
- 100% local — no cloud AI dependencies
- Privacy-first — your data never leaves your computer
- Fast — runs on your own hardware
- Free and open-source

### How does Dash-AI differ from ChatGPT/Claude/other AI services?

| Feature | Dash-AI | ChatGPT/Claude |
|---------|---------|---|
| **Privacy** | Local, no upload | Data sent to cloud |
| **Cost** | Free | Subscription required |
| **Internet** | Works offline | Requires internet |
| **Model** | Your choice (local) | Provider's model |
| **Data** | Stays on your computer | Stored on servers |
| **Customization** | Easy, local control | Limited |

Dash-AI is for cases where you want to keep your data private and control your own AI.

### Do I need internet to use Dash-AI?

**Short answer:** No, not after initial setup.

**Long answer:**
- First time: Yes, you need internet to download the LLM model (~4-8GB depending on model)
- After that: No, everything runs locally without internet
- Great for offline work: Airplanes, disconnected networks, secure environments

### How large can my knowledge base be?

Dash-AI has been tested with:
- **Single documents:** Up to 10MB each (larger works, but slower)
- **Total database:** Tested up to 100K+ chunks (~1GB of content)
- **Typical use:** 10-100MB of documents works great

Limitations depend on your available disk space and RAM.

---

## Installation & Setup

### What are the prerequisites?

1. **Python 3.10+** — [Install Python](https://www.python.org/downloads/)
2. **Ollama** — [Download Ollama](https://ollama.ai)
3. **A language model** — Download via Ollama (automatic, ~4-8GB)

That's it! No cloud account needed.

### How do I install Dash-AI?

```bash
# Clone the repository
git clone https://github.com/edgar-treischl/dash-ai.git
cd dash-ai

# Install with uv
uv sync

# Create config (optional, has defaults)
cp config/settings.yaml.example config/settings.yaml

# You're ready!
dash-ai --version
```

### How do I install it on Windows?

Dash-AI is built for Unix-like systems (macOS, Linux). On Windows:

**Option 1: WSL (Windows Subsystem for Linux)**
```bash
# Install WSL2: https://docs.microsoft.com/windows/wsl/install
# Install Ubuntu in WSL2
# Then follow Linux installation

# Note: Run Ollama on Windows host, point dash-ai to it:
# In WSL: OLLAMA_BASE_URL=http://host.docker.internal:11434
```

**Option 2: Docker**
```bash
# Run in container
docker run -v $(pwd)/data:/app/data -v $(pwd)/config:/app/config dash-ai
```

### How do I set up Ollama?

```bash
# macOS
# Download from https://ollama.ai and install

# Linux
curl https://ollama.ai/install.sh | sh

# Start Ollama
ollama serve

# Download a model
ollama pull llama2  # In another terminal

# Done! Ready to use Dash-AI
```

---

## Usage Questions

### How do I add documents to Dash-AI?

```bash
# Single file
dash-ai ingest my_document.md

# Multiple files
dash-ai ingest data/knowledge/

# Add to existing knowledge base (doesn't delete old docs)
dash-ai ingest new_documents/
```

Documents should be Markdown format (`.md` files).

### What file formats does Dash-AI support?

**Currently supported:**
- Markdown (`.md`)

**Planned:**
- PDF (Phase 3)
- Plain text (Phase 3)
- HTML (Phase 3)

**Workaround for PDF/other formats:**
- Convert to Markdown using tools like Pandoc:
  ```bash
  pandoc document.pdf -o document.md
  ```

### How do I ask questions?

```bash
# Single question
dash-ai ask "What is machine learning?"

# Interactive conversation
dash-ai chat

# Programmatic (Python)
from dash_ai import App
app = App()
answer = app.ask("Your question here")
print(answer.text)
```

### How do I get JSON output for automation?

```bash
# Add --json flag to any command
dash-ai ask "What is Python?" --json

# Output example:
# {
#   "status": "success",
#   "question": "What is Python?",
#   "answer": "Python is a high-level programming language...",
#   "sources": [...],
#   "generation_time_ms": 2345
# }
```

### How do I configure Dash-AI?

**Option 1: Config file**
```bash
# Edit config/settings.yaml
model:
  name: mistral  # Change model
  max_tokens: 2048

ollama:
  base_url: http://localhost:11434
```

**Option 2: Environment variables**
```bash
MODEL_NAME=mistral dash-ai ask "Your question"
OLLAMA_BASE_URL=http://custom-server:11434 dash-ai ask "Your question"
```

**Default config works for most users** — no setup needed!

---

## Model & Performance Questions

### Which language models work with Dash-AI?

Any model that Ollama supports. Popular choices:

| Model | Speed | Quality | Size | Best For |
|-------|-------|---------|------|----------|
| **mistral** | ⚡ Fast | Good | 5GB | Quick answers |
| **llama2** | Medium | Very Good | 4GB | General use (default) |
| **neural-chat** | Fast | Good | 5GB | Conversations |
| **orca-mini** | ⚡ Very Fast | Fair | 2GB | Limited resources |
| **dolphin-mixtral** | Slow | Excellent | 26GB | Best quality |

**Get started:**
```bash
# Try default (llama2)
ollama pull llama2

# Try faster option
ollama pull mistral

# See all available models
ollama list
```

### Can I use a different model than llama2?

Yes! Easy to change:

```bash
# Download the model
ollama pull mistral

# Use it
MODEL_NAME=mistral dash-ai ask "Your question"

# Or set as default in config/settings.yaml
```

### Why is it slow?

Typical response times:
- **Search:** < 50ms (instant)
- **Model generation:** 5-30s (depends on model, hardware, question)
- **Total:** < 35s for typical questions

**If slower:**
- Use faster model: `MODEL_NAME=mistral`
- Close other applications
- Check disk space
- See [Troubleshooting Guide](troubleshooting.md)

### How much disk space does Dash-AI need?

- **Installation:** ~100MB
- **Model (llama2):** ~4GB
- **Your documents:** Depends on what you ingest
- **Database:** ~1GB for ~100K chunks

**Total estimate:** 5-10GB for typical setup

### How much RAM do I need?

**Minimum:** 4GB  
**Recommended:** 8GB+  
**Ideal:** 16GB+

The language model takes up most of the RAM. Smaller models (mistral, orca-mini) use less RAM than larger ones.

---

## Data & Privacy Questions

### Is my data private?

**Yes, completely.** Your data:
- ✅ Stays on your computer
- ✅ Never uploaded to internet
- ✅ Never shared with anyone
- ✅ Only processed locally by Ollama
- ✅ Fully under your control

This is the core promise of Dash-AI.

### Can I export my documents?

```bash
# Export using sqlite3
sqlite3 ~/.local/share/dash-ai/db.sqlite \
  "SELECT source, content FROM documents;" \
  > exported_documents.txt

# Or use Python
from dash_ai import App
app = App()
documents = app.storage.get_all_documents()
for doc in documents:
    print(doc.content)
```

### Can I back up my knowledge base?

```bash
# Simple backup
cp -r ~/.local/share/dash-ai ~/.local/share/dash-ai.backup

# Or backup database only
cp ~/.local/share/dash-ai/db.sqlite ~/db.sqlite.backup
```

### How do I delete documents?

```bash
# Delete by ID
dash-ai delete document-id-here

# Delete all
dash-ai delete --all

# Delete database entirely
rm ~/.local/share/dash-ai/db.sqlite
```

### Where is my data stored?

**Linux/macOS:**
```
~/.local/share/dash-ai/
├── db.sqlite         # Main database
└── config/
    └── settings.yaml # Configuration
```

**Customizable via environment:**
```bash
DASH_AI_DATA_DIR=~/my_data_location dash-ai ask "question"
```

---

## Integration & Customization

### Can I use Dash-AI as a Python library?

Yes! Install it:

```bash
# From git
pip install -e git+https://github.com/edgar-treischl/dash-ai#egg=dash-ai

# Then use it
from dash_ai import App

app = App()
result = app.ask("What is Python?")
print(result.text)
print(result.sources)
```

See [Python API Guide](user_guide/api/python.md) for details.

### Can I add custom commands?

You can extend Dash-AI with custom logic:

```python
from dash_ai import App

class MyCustomApp(App):
    def summarize(self, query: str) -> str:
        """Custom method for summarization"""
        return self.ask(f"Summarize: {query}").text

app = MyCustomApp()
summary = app.summarize("my document")
```

### Can I use it for web applications?

Yes, via the Python API:

```python
# Flask example
from flask import Flask, request, jsonify
from dash_ai import App

app = Flask(__name__)
dash = App()

@app.route('/ask', methods=['POST'])
def ask_question():
    question = request.json.get('question')
    result = dash.ask(question)
    return jsonify({
        'answer': result.text,
        'sources': [s.source_file for s in result.sources]
    })
```

### Can I run multiple instances?

Yes, but they'll share the same database. For isolation:

```bash
# Use different data directories
DASH_AI_DATA_DIR=~/data1 dash-ai ask "question 1"
DASH_AI_DATA_DIR=~/data2 dash-ai ask "question 2"
```

---

## Advanced Questions

### How does Dash-AI retrieve relevant documents?

Dash-AI uses **full-text search** with Ollama's embedding capabilities:

1. **Index documents** — Splits into chunks, builds search index
2. **Search** — Finds chunks matching your question
3. **Generate** — LLM answers based on retrieved context
4. **Return** — Provides answer with source references

This is called a **RAG (Retrieval-Augmented Generation)** system.

### Can I use Dash-AI for real-time applications?

Dash-AI is designed for:
- ✅ Knowledge-based QA
- ✅ Offline AI assistant
- ✅ Document analysis
- ✅ Batch processing

Not ideal for:
- ❌ Real-time chat servers (slow)
- ❌ High-throughput APIs (designed for single user)
- ❌ Streaming responses (yet)

**Consider for scale:** Migrate to cloud AI or multi-instance setup.

### Can I use this with my company's documents?

**Yes!** Ideal for:
- ✅ Internal documentation
- ✅ Company handbook/knowledge base
- ✅ Codebase documentation
- ✅ Meeting notes and decision records

**Important:** Make sure you have rights to use the documents locally.

### What about model fine-tuning?

Currently, Dash-AI uses base models without fine-tuning. Future support planned for Phase 3:
- Custom fine-tuning on your documents
- Improved domain-specific answers

### Can I use Dash-AI offline completely?

**After initial setup:**
- ✅ Generate answers — fully offline
- ✅ Ingest new documents — fully offline
- ✅ Search knowledge base — fully offline

**Not offline:**
- ❌ Downloading models (needs internet)
- ❌ Updates (needs internet)

**Perfect for:** Airplanes, trains, remote locations (once set up).

---

## Troubleshooting Questions

### Ollama won't connect

**Quick fix:**
```bash
# Start Ollama
ollama serve

# In another terminal, test
curl http://localhost:11434/api/tags
```

See [Troubleshooting Guide](troubleshooting.md#connection-issues) for more help.

### My questions return empty results

**Check:**
1. Are documents ingested? `dash-ai list`
2. Search relevant? Try simpler terms: `dash-ai ask "simple term"`
3. Documents valid? Check file encoding: `file -i docs/*.md`

See [Troubleshooting Guide](troubleshooting.md#search--retrieval-issues) for more.

### Getting "database locked" error

**Quick fix:**
```bash
# Kill stuck process
pkill -f dash-ai

# Try again
dash-ai ask "your question"
```

See [Troubleshooting Guide](troubleshooting.md#database-locked) for more.

### How do I check the database?

```bash
# See documents
sqlite3 ~/.local/share/dash-ai/db.sqlite "SELECT COUNT(*) FROM documents;"

# See chunks
sqlite3 ~/.local/share/dash-ai/db.sqlite "SELECT COUNT(*) FROM chunks;"

# Check integrity
sqlite3 ~/.local/share/dash-ai/db.sqlite "PRAGMA integrity_check;"
```

---

## Development Questions

### How do I contribute?

See [Contributing Guide](user_guide/contributing/guide.md) for:
- Development setup
- Testing
- Pull request process
- Code style

### What's the roadmap?

See [Roadmap](user_guide/guides/roadmap.md) for:
- Phase 2: Error handling, interactive mode, JSON output
- Phase 3: PDF support, vector search, REST API
- Phase 4: Fine-tuning, plugins, cloud deployment

### How can I report a bug?

1. Check [Troubleshooting Guide](troubleshooting.md)
2. Search [GitHub Issues](https://github.com/edgar-treischl/dash-ai/issues)
3. Create new issue with:
   - Error message (full traceback)
   - Steps to reproduce
   - Your OS and Python version

### How do I request a feature?

1. Check [Roadmap](user_guide/guides/roadmap.md)
2. Discuss in [GitHub Discussions](https://github.com/edgar-treischl/dash-ai/discussions)
3. Open a [GitHub Issue](https://github.com/edgar-treischl/dash-ai/issues) with "Feature: " prefix

---

## Performance & Optimization

### How can I make it faster?

**Quick wins:**
1. Use faster model: `MODEL_NAME=mistral`
2. Close other applications
3. Ensure enough free disk space
4. Use SSD instead of HDD

**Configuration:**
```yaml
# config/settings.yaml
model:
  max_tokens: 256  # Smaller = faster
  temperature: 0.3  # Lower = faster (less random)
```

### How can I optimize for large documents?

```bash
# Break large files into smaller chunks
# Best: < 10MB per file

# Example with a large PDF (converted to markdown)
split -l 1000 large_document.md parts_
dash-ai ingest parts_*
```

### How do I monitor performance?

```bash
# Measure query time
time dash-ai ask "your question"

# Get detailed timing
dash-ai ask "your question" --verbose
# Shows: search time, model time, total time
```

---

## Comparison with Alternatives

### vs. Pinecone / Weaviate / Milvus (Vector Databases)

**Dash-AI advantages:**
- ✅ No setup required
- ✅ Works offline
- ✅ No subscription
- ✅ Simple to use

**Vector DB advantages:**
- ✅ Better search quality
- ✅ Scales to millions of documents
- ✅ Supports real-time streaming

**Use Dash-AI when:** Personal/small team knowledge base  
**Use Vector DB when:** Enterprise scale, advanced search

### vs. Obsidian / Notion / Roam Research (Note-taking)

**Note-taking tools are for:** Creating and organizing notes  
**Dash-AI is for:** Answering questions about existing notes

**Complement each other:** Use Obsidian to create notes, Dash-AI to query them.

### vs. Building custom RAG with LangChain

**LangChain is for:** Building complex AI applications  
**Dash-AI is for:** Simple, batteries-included knowledge assistant

**Dash-AI internally uses:** Similar patterns to LangChain, but simpler

---

## Licensing & Legal

### What license is Dash-AI under?

MIT License — free for personal and commercial use.  
See [LICENSE](../LICENSE) file for details.

### Can I use it commercially?

Yes! MIT license allows commercial use.

### Is there support?

**Community support:**
- GitHub Issues for bugs
- GitHub Discussions for questions
- Contributing community members

**No paid support yet,** but planned for Phase 4.

---

## Still Have Questions?

- 📖 Check the [User Guide](user_guide/guides/quickstart.md)
- 🔧 See [Troubleshooting Guide](troubleshooting.md)
- 💬 Ask in [GitHub Discussions](https://github.com/edgar-treischl/dash-ai/discussions)
- 🐛 Report bugs on [GitHub Issues](https://github.com/edgar-treischl/dash-ai/issues)

---

**Last updated:** October 31, 2024  
**Applies to:** Phase 2+
