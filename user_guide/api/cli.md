# CLI Reference

Run commands from the repository root. Use `make install` (`uv sync`) first.
`uv run` selects the project environment without needing to activate `.venv`.

All application commands require Ollama running and the configured model
installed. See [Quick Start](../guides/quickstart.md) for system installation,
`make start`, and `make pull`.

## Make targets

| Command | Purpose |
|---|---|
| `make help` | Show available targets (also the default for `make`) |
| `make install` | Install Python application dependencies |
| `make install-dev` | Install application and development dependencies |
| `make start` | Run `ollama serve` in the foreground |
| `make pull` | Download the configured model; requires a running server |
| `make ingest INPUT="path"` | Import one Markdown file or a directory |
| `make ask QUESTION="question"` | Ask about imported knowledge |
| `make list` | List imported files and chunk counts |
| `make test` | Run pytest with the `dev` extra |

`INPUT` defaults to `data/knowledge/example.md`. `QUESTION` defaults to
`What is this project about?`. Make does not start a background server or
download models automatically.

## `ingest`

```bash
uv run dash-ai ingest data/knowledge/example.md
uv run dash-ai ingest "path/to/notes"
```

Accepts exactly one file or directory path. Directories are searched recursively
for `.md` and `.markdown` files. Do not pass shell globs or multiple paths.
Documents are split into paragraph-based chunks and saved in SQLite.

Example output:

```text
✓ Imported 1 file(s) with 16 chunk(s)
```

Re-ingesting updates chunks with the same IDs. It does not remove leftover
chunks if the new version contains fewer chunks.

## `ask`

```bash
uv run dash-ai ask "What is this project about?"
uv run dash-ai ask "How does storage work?" --top-k 3
```

Accepts one quoted question. `-k` / `--top-k` sets the maximum number of
retrieved chunks (default: `retrieval.top_k` in configuration).
Search matches individual query words using SQLite full-text search, then sends
matching chunks to Ollama for generation. This is not semantic/vector search.

Example output:

```text
Answer: [Generated answer]

Sources:
- data/knowledge/example.md (chunk 0)
```

If retrieval finds no matches, the command prints:

```text
I couldn't find any relevant information to answer your question.
```

## `list`

```bash
uv run dash-ai list
```

Lists source files, chunk counts, and size in KB. If the database is empty,
prints `No documents imported yet.`

## `delete`

```bash
uv run dash-ai delete example_0
```

Accepts a stored document/chunk ID, not a source filename. Removes that single
chunk from storage and its search index; it does not delete the original file.
The current `list` command groups chunks by source and does not display IDs.
To inspect IDs using the Python API:

```bash
uv run python -c 'from dash_ai.app import App; print([(doc.id, doc.source) for doc in App().storage.list_documents()])'
```

## Help

```bash
uv run dash-ai --help
uv run dash-ai ask --help
```

`-h` / `--help` is supported. There is no `--version` option.

## Configuration

Settings are loaded from `config/settings.yaml` and can be overridden via
environment variables or `.env`:

```bash
MODEL_NAME=mistral uv run dash-ai ask "What is this project about?"
OLLAMA_HOST=http://localhost:11434 make pull
STORAGE_PATH=./data/other.db uv run dash-ai list
```

Supported overrides are `MODEL_NAME`, `OLLAMA_HOST`, `STORAGE_PATH`, `DATA_DIR`,
and `DEBUG`. See [Configuration](../guides/configuration.md) for details.

## Troubleshooting

- **Ollama missing:** Install it separately; `uv sync` only installs Python dependencies.
- **Cannot connect:** Run `make start` in another terminal and check `model.host`.
- **Model missing:** Run `make pull` while the configured server is running.
- **No relevant information:** Run `make list`, ingest relevant files, and ask using words present in them.
- **File not found:** Pass an existing file or directory, relative to the repository root or absolute.
- **Database locked:** Wait for active operations to finish and retry.
