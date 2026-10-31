# Troubleshooting Guide

This guide covers common issues you might encounter when using Dash-AI and how to fix them.

---

## Connection Issues

### "Ollama connection refused" or "Failed to connect to Ollama"

**Symptoms:**
- Error message: `Failed to connect to Ollama at http://localhost:11434`
- CLI fails on `ask` or `chat` commands
- No response from the model

**Solutions:**

1. **Check if Ollama is running:**
   ```bash
   # macOS / Linux
   curl http://localhost:11434/api/tags
   
   # Should see JSON output with available models
   ```

2. **Start Ollama if not running:**
   ```bash
   # macOS - if installed via app
   # Just open the Ollama application
   
   # Linux
   ollama serve
   ```

3. **Check Ollama is on the right port:**
   - Default: `http://localhost:11434`
   - If you changed it, update `config/settings.yaml`:
     ```yaml
     ollama:
       base_url: http://your-custom-url:port
     ```

4. **Check network connectivity:**
   ```bash
   # Ensure you can reach localhost
   telnet localhost 11434
   # Should connect; press Ctrl+C to exit
   ```

5. **On Windows/WSL:**
   - Ensure WSL has network access to Windows host
   - Use `http://host.docker.internal:11434` if running Ollama on Windows
   - Or use `http://127.0.0.1:11434` if Ollama runs inside WSL

---

## Model Issues

### "Model not found" or "pull access denied"

**Symptoms:**
- Error: `Model 'llama2' not found`
- `ask` or `chat` commands fail immediately
- Model seems to be unloaded

**Solutions:**

1. **List available models:**
   ```bash
   ollama list
   ```

2. **Download the model you want:**
   ```bash
   # Download a model (choose one)
   ollama pull llama2
   ollama pull mistral
   ollama pull neural-chat
   ```

3. **Check your config:**
   - Verify `MODEL_NAME` in `config/settings.yaml` matches an installed model:
     ```yaml
     model:
       name: llama2  # Must match output of 'ollama list'
     ```

4. **Use environment override:**
   ```bash
   # Temporarily use a different model
   MODEL_NAME=mistral dash-ai ask "What is Python?"
   ```

5. **Common models to try:**
   - `llama2` — Fast, good general-purpose (default)
   - `mistral` — Faster, smaller, good for quick responses
   - `neural-chat` — Good for conversations
   - `orca-mini` — Smallest, best for limited resources

---

## Search & Retrieval Issues

### "Empty search results" or "No relevant documents found"

**Symptoms:**
- Ask a question but get "No documents found" or empty answer
- You know you ingested documents, but they're not being retrieved
- Answer is generic or unhelpful

**Causes & Solutions:**

1. **Check if documents were ingested:**
   ```bash
   dash-ai list
   # Should show your documents
   ```
   
   If nothing shows, re-ingest:
   ```bash
   dash-ai ingest data/knowledge/
   ```

2. **Check search index:**
   - Full-text search may not find results if:
     - Query terms don't match document content
     - Documents are chunked and chunks don't contain full context
     - Query is too vague or different from document language
   
   **Fix:** Try more specific search terms or ingest more relevant documents.

3. **Verify documents contain expected content:**
   ```bash
   dash-ai list --json | head -5
   # Check the document sources and metadata
   ```

4. **Re-index if search seems broken:**
   ```bash
   # Backup your database
   cp ~/.local/share/dash-ai/db.sqlite ~/.local/share/dash-ai/db.sqlite.backup
   
   # Clear and re-ingest documents
   rm ~/.local/share/dash-ai/db.sqlite
   dash-ai ingest data/knowledge/
   ```

5. **Try simpler queries:**
   ```bash
   # Instead of: "How does the recursive algorithm optimize tail calls?"
   # Try: "recursive algorithm"
   # Then: "tail call optimization"
   ```

6. **Check document format:**
   - Ensure Markdown files are valid UTF-8
   - Check for corruption: `file data/knowledge/*.md`

---

## Performance Issues

### "Slow response" or "Takes > 30 seconds to answer"

**Symptoms:**
- `dash-ai ask` hangs or takes very long
- Model seems to be generating forever
- Process uses high CPU

**Typical Performance:**
- Search: < 50ms
- Model generation: 5–30s (depends on model and question)
- Total: < 35s for typical questions

**Solutions:**

1. **Check which component is slow:**
   ```bash
   # Check search time separately
   dash-ai ask "search term" --json
   # Look at "generation_time_ms" field
   ```

2. **Use a faster model:**
   ```bash
   ollama pull mistral  # Faster than llama2
   
   # Update config or use override
   MODEL_NAME=mistral dash-ai ask "your question"
   ```

3. **Reduce document set:**
   - If you have many documents, search time increases
   - Delete unused documents: `dash-ai delete --all` and re-ingest selectively

4. **Optimize your documents:**
   - Remove very large files (> 1MB): Break into smaller parts
   - Remove duplicate content: Consolidate redundant documents
   - Check for corrupt/malformed Markdown

5. **Check system resources:**
   ```bash
   # macOS
   top -l 1 | grep "Mem\|Swap"
   
   # Linux
   free -h
   
   # If memory low, close other apps and try again
   ```

6. **Increase model context if you have it:**
   - Some models support larger context windows
   - Larger context = slower responses
   - If possible, use smaller context

7. **Profile the issue:**
   ```bash
   # Check database performance
   sqlite3 ~/.local/share/dash-ai/db.sqlite "PRAGMA query_only=ON; SELECT count(*) FROM chunks;"
   # If very large (> 1M chunks), consider archiving old data
   ```

---

## Storage & Database Issues

### "Database locked" or "Cannot write to database"

**Symptoms:**
- Error: `database is locked`
- Can't ingest new documents
- Commands fail randomly

**Causes & Solutions:**

1. **Close other dash-ai processes:**
   ```bash
   # Check for running processes
   ps aux | grep dash-ai
   
   # Kill if stuck
   pkill -f dash-ai
   ```

2. **Check file permissions:**
   ```bash
   ls -la ~/.local/share/dash-ai/
   # Should show your user ownership
   
   # Fix if needed
   chmod 600 ~/.local/share/dash-ai/db.sqlite
   chmod 700 ~/.local/share/dash-ai/
   ```

3. **Check disk space:**
   ```bash
   df -h ~
   # If < 100MB free, delete some documents or data
   ```

4. **Repair database if corrupted:**
   ```bash
   # Backup first
   cp ~/.local/share/dash-ai/db.sqlite ~/.local/share/dash-ai/db.sqlite.backup
   
   # Check integrity
   sqlite3 ~/.local/share/dash-ai/db.sqlite "PRAGMA integrity_check;"
   
   # If shows "ok", database is fine
   # If errors, restore backup and clear: rm db.sqlite
   ```

---

### "Out of memory" or "Process killed"

**Symptoms:**
- Process terminates unexpectedly
- Error: `Killed` or `Out of memory`
- System becomes unresponsive

**Causes & Solutions:**

1. **Check available memory:**
   ```bash
   # macOS
   vm_stat | grep "Pages free"
   
   # Linux
   free -h
   ```

2. **Reduce ingestion batch size:**
   - Large files (> 100MB) may exhaust memory
   - Split into smaller files (< 10MB each)
   ```bash
   # Check file sizes
   du -h data/knowledge/*
   ```

3. **Clear old data:**
   ```bash
   # Delete unneeded documents
   dash-ai delete <document-id>
   ```

4. **Use smaller model:**
   ```bash
   ollama pull orca-mini  # Much smaller than llama2
   MODEL_NAME=orca-mini dash-ai ask "your question"
   ```

5. **Increase available system memory:**
   - Close other applications
   - Increase swap (if on Linux)
   - Consider machine with more RAM for deployment

---

## Input & Encoding Issues

### "Invalid UTF-8" or "Encoding error"

**Symptoms:**
- Error: `invalid UTF-8`
- Corruption or garbled text in results
- Specific files fail to ingest

**Solutions:**

1. **Check file encoding:**
   ```bash
   # macOS / Linux
   file -i data/knowledge/*.md
   # Should show "charset=utf-8"
   ```

2. **Convert files to UTF-8:**
   ```bash
   # Single file
   iconv -f ISO-8859-1 -t UTF-8 input.md > output.md
   mv output.md input.md
   
   # All files in directory
   for file in data/knowledge/*.md; do
     iconv -f ISO-8859-1 -t UTF-8 "$file" > "$file.utf8" && mv "$file.utf8" "$file"
   done
   ```

3. **Remove problematic characters:**
   ```bash
   # Check for bad bytes
   grep --color='auto' -n -P -o "[\x80-\xFF]" data/knowledge/*.md
   
   # Remove non-ASCII (if acceptable)
   iconv -f UTF-8 -t UTF-8 -c data/knowledge/file.md > data/knowledge/file.md.clean
   ```

---

### "Malformed Markdown" or "Parsing failed"

**Symptoms:**
- Error: `Invalid markdown` or `Parse error`
- Documents fail to ingest
- Specific sections cause problems

**Solutions:**

1. **Validate Markdown syntax:**
   ```bash
   # Use an online validator or local tool
   # Check for common issues:
   # - Unclosed code blocks (```)
   # - Unmatched brackets/parentheses
   # - Invalid link syntax
   ```

2. **Fix common Markdown errors:**
   ```markdown
   # ❌ Bad
   This is [a link](url
   
   # ✅ Good
   This is [a link](url)
   
   # ❌ Bad
   ```python
   code without closing fence
   
   # ✅ Good
   ```python
   code
   ```
   ```

3. **Check for special characters:**
   - Curly quotes: Replace `"` and `"` with `"`
   - Em dashes: Replace `–` or `—` with `--` if needed
   - Non-breaking spaces: Can cause issues

4. **Simplify problematic files:**
   - Remove complex formatting
   - Break into smaller sections
   - Test each section separately

---

## Configuration Issues

### "Settings not found" or "Invalid configuration"

**Symptoms:**
- Error: `Config not found` or `Invalid YAML`
- Settings don't take effect
- Can't find `config/settings.yaml`

**Solutions:**

1. **Verify config file exists:**
   ```bash
   # Should be in project root or XDG config directory
   ls -la config/settings.yaml
   # or
   ls -la ~/.config/dash-ai/settings.yaml
   ```

2. **Check YAML syntax:**
   - Use online YAML validator
   - Ensure proper indentation (spaces, not tabs)
   - Quote values with special characters
   ```yaml
   # ❌ Bad (tab indentation)
   ollama:
   	base_url: http://localhost:11434
   
   # ✅ Good (space indentation)
   ollama:
     base_url: http://localhost:11434
   ```

3. **Use environment overrides:**
   ```bash
   # Override settings without config file
   MODEL_NAME=mistral dash-ai ask "question"
   OLLAMA_BASE_URL=http://localhost:11434 dash-ai ask "question"
   ```

4. **Reset to defaults:**
   ```bash
   rm config/settings.yaml
   # App will use defaults or create a new config
   ```

---

## Command-Specific Issues

### `dash-ai ingest` — "Failed to ingest documents"

**Symptoms:**
- Error: `Ingestion failed` or `Cannot read file`
- Some files ingest, others fail
- Progress stops mid-operation

**Solutions:**

1. **Check file paths:**
   ```bash
   # Verify directory/files exist
   ls -la data/knowledge/
   ```

2. **Check file permissions:**
   ```bash
   # Ensure readable
   chmod 644 data/knowledge/*.md
   ```

3. **Try single file:**
   ```bash
   # Instead of directory, try specific file
   dash-ai ingest data/knowledge/single_file.md
   ```

4. **Check file size:**
   ```bash
   # Very large files may fail
   du -h data/knowledge/*
   # Should be < 10MB each
   ```

5. **Ingest with verbose output:**
   ```bash
   dash-ai ingest data/knowledge/ --verbose
   # Shows which files fail and why
   ```

---

### `dash-ai ask` — "Empty or unhelpful answer"

**Symptoms:**
- Gets an answer, but it's generic or off-topic
- Ignores your documents
- Answers like a generic chatbot

**Solutions:**

1. **Ensure documents are ingested:**
   ```bash
   dash-ai list
   ```

2. **Check search results:**
   ```bash
   dash-ai ask "your question" --verbose
   # Shows which documents were searched
   ```

3. **Ask more specific questions:**
   - Generic: "Tell me about Python"
   - Better: "What is Python's GIL?"

4. **Add more relevant documents:**
   - Model can only answer about ingested content
   - Ingest more specific knowledge: `dash-ai ingest docs/`

---

### `dash-ai chat` — "Interactive mode not working"

**Symptoms:**
- Command doesn't start
- Input doesn't work
- Terminal is unresponsive

**Solutions:**

1. **Ensure chat mode is supported:**
   ```bash
   dash-ai --version
   # Should show Phase 2+ version
   ```

2. **Check terminal compatibility:**
   - Use standard terminal (not exotic editor terminals)
   - Ensure TTY support: run from real terminal, not IDE output pane

3. **Exit properly:**
   - Type `exit` or `quit`
   - Or press Ctrl+D
   - Don't use Ctrl+C (may leave database locked)

---

## Advanced Troubleshooting

### Enable verbose logging

```bash
# Run with verbose output
dash-ai ask "question" --verbose

# Or set environment variable
DEBUG=1 dash-ai ask "question"
```

### Check database contents

```bash
# View documents table
sqlite3 ~/.local/share/dash-ai/db.sqlite "SELECT id, source, created_at FROM documents LIMIT 10;"

# View chunks
sqlite3 ~/.local/share/dash-ai/db.sqlite "SELECT id, document_id, content FROM chunks LIMIT 5;"

# Check full-text search index
sqlite3 ~/.local/share/dash-ai/db.sqlite "SELECT COUNT(*) FROM fts_chunks;"
```

### Test Ollama directly

```bash
# Generate without dashboard-ai
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model": "llama2", "prompt": "Hello", "stream": false}'
```

### Check logs

```bash
# If app logs to file
tail -f ~/.local/share/dash-ai/logs/app.log

# Or check system logs (Linux)
journalctl -u ollama
```

---

## When All Else Fails

### Reset everything

```bash
# Backup your documents first!
cp -r data/knowledge data/knowledge.backup

# Remove all dash-ai data
rm -rf ~/.local/share/dash-ai/
rm -rf ~/.config/dash-ai/

# Clear any caches
rm -rf .pytest_cache __pycache__

# Reinstall if needed
uv sync

# Start fresh
dash-ai ingest data/knowledge.backup/
```

### Contact support

If you've tried everything:
1. Check GitHub issues: [dash-ai/issues](https://github.com/edgar-treischl/dash-ai/issues)
2. Search for similar problems
3. If needed, create a new issue with:
   - Error message (full traceback)
   - `dash-ai --version`
   - OS and Python version: `python --version`
   - Steps to reproduce
   - Output of `dash-ai list`

---

## Quick Reference

| Problem | Quick Fix |
|---------|-----------|
| Ollama not responding | `ollama serve` |
| Model not found | `ollama pull llama2` |
| No documents found | `dash-ai ingest data/knowledge/` |
| Slow response | Try `MODEL_NAME=mistral` |
| Database locked | `pkill -f dash-ai` |
| Out of memory | Close apps, use smaller model |
| Encoding error | Ensure UTF-8: `file -i *.md` |
| Settings not working | Use env vars: `MODEL_NAME=mistral` |

---

**Last updated:** October 31, 2024  
**Applies to:** Phase 2+
