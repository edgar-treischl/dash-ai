# Quick Start

Run all project commands from the repository root.

## 1. Install

Prerequisites: Python 3.10+, [uv](https://docs.astral.sh/uv/getting-started/installation/),
[Ollama](https://ollama.com/download), and `make`.

On macOS with Homebrew:

```bash
brew install uv ollama
```

On Linux, install uv and Ollama using their linked installation instructions,
and install `make` with your system package manager.

Install the Python application:

```bash
make install
# Equivalent: uv sync
```

Ollama is a separate system application, not a Python dependency. Neither
`uv sync` nor activating `.venv` installs it. Make targets use `uv run`, so
you do not need to activate the virtual environment.

## 2. Start Ollama (terminal 1)

```bash
make start
# Equivalent: ollama serve
```

Leave this terminal running; Ctrl-C stops the server. By default, it listens on
`http://localhost:11434`. If the Ollama desktop app or a service is already
serving on that port, do not start another server.

## 3. Download the model (terminal 2)

From the repository root in a second terminal:

```bash
make pull
# With the default configuration, equivalent to: ollama pull mistral
```

This reads the model name from `config/settings.yaml`, including the `MODEL_NAME`
environment override. Download the model once; repeat if you change the model.
The first download can take several minutes.

All application commands currently check that Ollama is running and the
configured model is installed, even `ingest`, `list`, and `delete`.

## 4. Ingest knowledge

```bash
# Import the sample file
make ingest

# Import your own file
make ingest INPUT="path/to/notes.md"

# Recursively import all Markdown files in a directory
make ingest INPUT="path/to/notes"
```

Direct CLI equivalents:

```bash
uv run dash-ai ingest data/knowledge/example.md
uv run dash-ai ingest "path/to/notes"
```

`ingest` accepts one file or directory, not multiple file arguments or shell
globs. Data is stored locally at `./data/knowledge.db` by default.

## 5. Ask questions

```bash
make ask QUESTION="What is this project about?"
# Equivalent:
uv run dash-ai ask "What is this project about?"
```

Ask about information present in the imported documents. Retrieval matches
individual words and ranks matching chunks; it is full-text search, not
semantic/vector search.

Example output:

```text
Answer: [AI-generated answer based on your documents]

Sources:
- data/knowledge/example.md (chunk 0)
- data/knowledge/example.md (chunk 3)
```

## Other commands

```bash
make list
uv run dash-ai --help

# Delete one stored chunk by its document ID, not its source filename
uv run dash-ai delete example_0

make help
make install-dev
make test
```

Development dependencies are defined in the `dev` extra. `make install-dev`
uses `uv sync --extra dev`; plain `uv sync` removes these optional packages.
`make test` uses `uv run --extra dev pytest` so test dependencies are available.

## Subsequent sessions

Start Ollama if it is not already running (`make start` in terminal 1), then
use `make ask` in terminal 2. You do not need to reinstall dependencies,
download the same model, or re-ingest unchanged files each time.

## Troubleshooting

**`ollama: command not found`:** Install Ollama separately (on macOS:
`brew install ollama`). If already installed, check that its executable is
on your shell's `PATH`.

**Cannot connect to Ollama:** Keep `make start` running in another terminal.
Check `model.host` in `config/settings.yaml` (default:
`http://localhost:11434`).

**Address already in use:** Ollama may already be running via its desktop app
or a service. Check `curl http://localhost:11434/api/tags` before starting
another server.

**Model not found:** Run `make pull` while Ollama is running. If you change
`model.name` in `config/settings.yaml`, download the new model too.
For a remote Ollama server, set `OLLAMA_HOST` to the same server when running
`make pull` and application commands.

**No relevant information:** Check `make list`, import the relevant documents,
and include words that appear in them. Full-text search does not infer synonyms.

**Database locked:** Wait for active operations to finish and retry.

See [Configuration](configuration.md) for settings and the
[CLI Reference](../api/cli.md) for commands.
