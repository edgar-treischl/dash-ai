# Configuration Guide

Run commands from the repository root. The application reads
`config/settings.yaml`; a missing file or required field is an error, not a
fallback to defaults.

## Default configuration

```yaml
model:
  type: ollama
  name: mistral
  host: http://localhost:11434

storage:
  type: sqlite
  path: ./data/knowledge.db

retrieval:
  top_k: 5
  min_relevance: 0.0

app:
  data_dir: ./data/knowledge/
  debug: false
```

`model.host` is a complete URL, including the scheme and port.
`retrieval.top_k` controls how many matching chunks are passed to the model.
The ingestion path comes from the CLI argument (`make ingest INPUT="path"`),
not `app.data_dir`.

Currently, the application uses SQLite, Ollama, and Markdown readers.
`model.type` and `storage.type` are validated configuration fields but do not
yet select alternative implementations. `min_relevance`, `data_dir`, and `debug`
are loaded but do not currently change application behavior.
Model timeout/retries and chunk size are not configurable through YAML.

## Environment overrides

Shell environment variables take precedence over `.env` values; both override
YAML. Supported names:

| Variable | Configuration field |
|---|---|
| `MODEL_NAME` | `model.name` |
| `OLLAMA_HOST` | `model.host` |
| `STORAGE_PATH` | `storage.path` |
| `DATA_DIR` | `app.data_dir` |
| `DEBUG` | `app.debug` |

Example `.env`:

```dotenv
MODEL_NAME=mistral
OLLAMA_HOST=http://localhost:11434
STORAGE_PATH=./data/knowledge.db
```

For questions, `--top-k` overrides the configured retrieval count:

```bash
uv run dash-ai ask "How does storage work?" --top-k 3
```

## Change the model

Change `model.name` in YAML, then run `make pull` with Ollama running.
Alternatively, use the same override for downloading and asking:

```bash
MODEL_NAME=neural-chat make pull
MODEL_NAME=neural-chat make ask QUESTION="What is this project about?"
```

The default model name is `mistral`. Model availability checks currently
expect an untagged name (for example, `mistral`, not `mistral:latest`).

## Use a remote Ollama server

Use the same host for the model download and application:

```bash
OLLAMA_HOST=http://192.168.1.100:11434 make pull
OLLAMA_HOST=http://192.168.1.100:11434 make ask QUESTION="What is this project about?"
```

`make start` starts a server on this machine; it does not start a remote server.
If you set a remote host only in YAML or `.env`, also export `OLLAMA_HOST` when
running `make pull`, because the Ollama CLI does not read the project config.
Using a remote host sends retrieved context to that server; keep the default
localhost address for local-only processing.

## Use another database

```bash
STORAGE_PATH=./data/other.db make ingest INPUT="path/to/notes"
STORAGE_PATH=./data/other.db make ask QUESTION="What do my notes say?"
```

Use the same path when ingesting, listing, and asking. Parent directories and
database tables are created automatically. Relative paths resolve from the
current working directory.

See [Quick Start](quickstart.md) for installation and the two-terminal workflow.
