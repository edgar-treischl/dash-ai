# Performance Profiling Results

## Scope and method

Profiled the application-layer `ingest_files`, `list_documents`, and
`ask_question` workflows on 2026-10-31 using `cProfile`, `time.perf_counter`,
`time.process_time`, and `tracemalloc`. The fixture corpus contained 100
Markdown files, each producing two chunks (200 documents total), on Apple M5
Pro, macOS 26.6.2, Python 3.12.14, and SQLite 3.53.1.

The database and corpus were created in a temporary directory. For `ask`, the
Ollama model was replaced by a deterministic local stub, so the profile covers
retrieval, prompt construction, and answer formatting but **not model loading,
network time, or token generation**. Ollama was not running during profiling.
Times are single-run local baselines, not CI thresholds. `tracemalloc` reports
Python-tracked peak allocations; it does not include SQLite's native memory.

## Results

| Workflow | Wall time | Process CPU | Python peak | Notes |
|---|---:|---:|---:|---|
| Ingest, before batching | 98.5 ms | 87.5 ms | 198.8 KiB | 200 individual document saves |
| Ingest, after batching | 64.5 ms | 59.3 ms | 178.3 KiB | One batch save per file; 100 commits |
| List 200 chunks | 2.4 ms | 2.4 ms | 303.8 KiB | Loads and groups all documents |
| Ask 200 chunks | 0.7 ms | 0.7 ms | 42.5 KiB | Uses deterministic local model stub |

Batching lowered measured ingestion wall time by approximately 35% and Python
peak allocations by approximately 10%. These values are specific to this
machine and small corpus; compare trends under the same environment rather than
treating them as portable performance guarantees.

## Bottlenecks and changes

Before the change, ingestion called `save_document` for each chunk. Each call
opened a connection, executed document and FTS writes, and committed. In the
profile, 200 commits accounted for about 41 ms; SQLite execution accounted for
another 30 ms. The application now submits all chunks from a Markdown file
through `StorageInterface.save_documents`. The SQLite implementation uses
`executemany` and a single transaction per file. Other storage implementations
inherit a compatibility fallback that calls `save_document` per item.

The post-change profile still spends most ingestion time in SQLite commits and
statements, but halves the number of transactions for this two-chunk-per-file
workload. Batching across the whole directory could reduce commits further,
but would retain all parsed documents until ingestion finishes and would change
the current per-file persistence boundary. That trade-off was not made.

`list_documents` and local retrieval/answer orchestration were below 3 ms for
this corpus and did not reveal a worthwhile optimization. Search already uses
the FTS5 index and a parameterized `LIMIT`, and the documents table primary key
is indexed; no additional index or search cache was justified by this profile.
Markdown parsing and chunking took about 10 ms across the 100 files and were
not the dominant cost.

## Reproducing

Run the application under a profiler with a representative corpus and a
temporary database. For example:

```bash
uv run --extra dev python -m cProfile -s cumulative path/to/profile_workload.py
```

Measure wall-clock and Python memory separately when needed:

```python
import time
import tracemalloc

tracemalloc.start()
started = time.perf_counter()
run_workload()
wall_seconds = time.perf_counter() - started
_, peak_bytes = tracemalloc.get_traced_memory()
tracemalloc.stop()
```

For a true end-to-end `ask` profile, start Ollama with the configured model and
measure inference separately from retrieval. Local model runtime, model size,
hardware, and prompt length dominate that latency and are not represented by
the stubbed result above.
