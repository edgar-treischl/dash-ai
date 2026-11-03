# React + TypeScript + Vite

I'm building a lightweight web interface for an existing Python-based local LLM/RAG POC.

Current backend:

Python application with Markdown-only document ingestion.
Local LLM inference using Ollama.
Existing RAG pipeline.
JSON responses already implemented.
Currently CLI-based.

Objective: Build a minimal browser-based LLM Playground to test questions, display answers, inspect JSON responses and visualize document sources.

Frontend stack:

React + Vite + TypeScript.
Native CSS (no Tailwind or UI libraries).
Yarn.

Architecture requirements:

Frontend must be completely independent of backend implementation.
Communication exclusively through HTTP/JSON APIs.
No direct dependencies on Python, Ollama or RAG internals.
Frontend should eventually be reusable in the production React website.
Frontend lives in its own subfolder within the existing repository.

Development approach: Keep everything lightweight. First implement the chat interface, connect the existing API, display answers and raw JSON, then progressively add sources, streaming and deployment capabilities.

Long-term vision: A self-hosted, independently deployable LLM/RAG web service running on infrastructure we control.