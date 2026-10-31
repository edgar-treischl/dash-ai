# Performance

## Current profile

The application has fast local storage and retrieval for small-to-medium
knowledge bases. In a local profile of 100 Markdown files (200 chunks),
ingestion completed in 64.5 ms after batching storage writes, listing took
2.4 ms, and retrieval plus answering orchestration took 0.7 ms with a
deterministic model stub. These are machine-specific measurements; the ask
measurement excludes Ollama inference. See
[profiling results](profiling_results.md) for the environment and methodology.

The performance tests in `tests/test_performance_benchmarks.py` provide
regression bounds for ingestion, search, retrieval, and database operations.
Run them with:

```bash
uv run --extra dev pytest tests/test_performance_benchmarks.py
```

## Implementation notes

- Markdown chunks from each file are saved in one SQLite transaction. This
  avoids opening and committing once per chunk while retaining per-file
  ingestion boundaries.
- Full-text search uses SQLite FTS5 and limits returned rows with `top_k`.
- The documents table primary key provides its ID index; profiling did not
  justify another index or a search-result cache.
- Listing currently loads document content to group chunks by source. At the
  measured scale this remained below 3 ms. For substantially larger databases,
  consider a storage-level aggregate query before adding caching.

## Future profiling

For large corpora, profile ingestion with representative file sizes and chunk
counts, and inspect both Python allocations and process memory. To assess
answer latency, profile with the actual Ollama model and report retrieval,
prompt construction, and model inference separately. Consider directory-wide
batching only if measurements justify the additional memory use and changed
per-file persistence behavior.
