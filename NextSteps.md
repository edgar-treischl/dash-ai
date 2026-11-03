# Local LLM / RAG POC – Improvement Roadmap

Goal: Evolve the existing FastAPI + Vite + Ollama + SQLite prototype into a more capable local LLM application while learning about local inference, RAG and model optimization.

## Phase 1 – Core POC improvements
- [ ] Model configuration (model selection, temperature, context length, parameters)
- [ ] Centralized prompt management (system prompts, templates)
- [ ] LLM runtime abstraction (Ollama initially, MLX / llama.cpp later)
- [ ] Improve streaming of the return; check error handling
- [ ] Conversation history and persistence

## Phase 2 – Advanced RAG
- [ ] Improve document ingestion and structure-aware chunking
- [ ] Add document metadata and filtering
- [ ] Implement vector search improvements
- [ ] Introduce hybrid search (vector + BM25)
- [ ] Experiment with reranking
- [ ] Improve source citations and traceability
- [ ] Handle document updates and versioning

## Phase 3 – RAG evaluation
- [ ] Create a representative question/answer evaluation dataset
- [ ] Measure retrieval precision and recall
- [ ] Evaluate answer relevance and faithfulness
- [ ] Compare chunking and retrieval strategies
- [ ] Benchmark different embedding models

## Phase 4 – Local LLM experimentation
- [ ] Compare Ollama, MLX and llama.cpp
- [ ] Benchmark different models and quantizations
- [ ] Measure tokens/second and time to first token
- [ ] Monitor RAM / unified memory consumption
- [ ] Compare response quality and inference performance

## Phase 5 – Monitoring & observability
- [ ] Build a lightweight monitoring dashboard
- [ ] Track inference latency and token throughput
- [ ] Monitor CPU, RAM and unified memory
- [ ] Track model usage and request counts
- [ ] Log retrieval results and relevance scores
- [ ] Visualize errors and failed requests
- [ ] Inspect prompts, retrieved context and generated answers

## Phase 6 – Preparation for deployment
- [ ] Configuration-driven application setup
- [ ] Persistent storage and backup strategy
- [ ] Authentication and access control
- [ ] Dockerize FastAPI and frontend
- [ ] Prepare production configuration
- [ ] Evaluate EU hosting options

## Deliberately postponed
- PostgreSQL / alternative storage backends
- Dedicated vector databases
- Custom training and fine-tuning infrastructure
- Kubernetes and complex orchestration
- Production GPU infrastructure

**Guiding principle:** Improve one capability at a time, measure its impact, document the results and keep the existing POC working throughout development.