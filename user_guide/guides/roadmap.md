# Roadmap

Future phases and planned features.

## Phase 1 ✅ Complete

**End-to-End RAG System**

- [x] Core interfaces and architecture
- [x] YAML configuration with validation
- [x] Markdown ingestion with paragraph chunking
- [x] SQLite storage with FTS5 full-text search
- [x] Ollama LLM integration
- [x] RAG question-answering pipeline
- [x] CLI with 4 commands (ingest, ask, list, delete)
- [x] Comprehensive test suite (79 tests, 90% coverage)

**Current Status:** Production-ready for single-user local use.

---

## Phase 2 📋 Planned

**Enhanced User Experience & Performance**

### CLI Improvements
- [ ] Interactive CLI with command history
- [ ] JSON output format for scripting
- [ ] Streaming responses (real-time answer generation)
- [ ] Progress indicators for ingestion
- [ ] Colored output with formatting
- [ ] Shell completion (bash/zsh/fish)

### Search & Retrieval
- [ ] Chunking strategy options (semantic, sliding window)
- [ ] Configurable search weights (title > content)
- [ ] Query expansion and synonym support
- [ ] Search performance benchmarks
- [ ] Result filtering by document/date

### Input Formats
- [ ] PDF ingestion with text extraction
- [ ] CSV/TSV import
- [ ] JSON document format
- [ ] Plain text files
- [ ] Web content scraping

### Performance
- [ ] Lazy loading of document content
- [ ] Database query optimization
- [ ] Batch ingestion improvements
- [ ] Concurrent processing
- [ ] Caching for frequent queries

### Monitoring & Debugging
- [ ] Query logging and history
- [ ] Performance metrics dashboard
- [ ] Debug mode with detailed logs
- [ ] Statistics: queries/day, avg response time, etc.

### Configuration Enhancements
- [ ] Config profiles (dev, production, testing)
- [ ] Configuration UI or wizard
- [ ] Settings validation and suggestions
- [ ] Hot-reload without restart

**Estimated Timeline:** Q1 2025

---

## Phase 3 🚀 Aspirational

**Advanced AI Capabilities & Scalability**

### Vector Search & Embeddings
- [ ] Vector embedding support (Ollama embed)
- [ ] Semantic search alongside FTS5
- [ ] Hybrid search combining both methods
- [ ] Embedding model selection
- [ ] Vector database backend (Qdrant, Milvus, etc.)

### Multi-Model Support
- [ ] Support for llama.cpp
- [ ] Support for MLX framework
- [ ] Model hot-swapping
- [ ] Per-query model selection
- [ ] Local model download/management

### Advanced RAG Features
- [ ] Multi-turn conversations with context
- [ ] Query refinement and clarification
- [ ] Confidence scoring in answers
- [ ] Citation strength validation
- [ ] Fact-checking against sources
- [ ] Answer summarization

### Storage & Scalability
- [ ] PostgreSQL backend with pgvector
- [ ] Horizontal scaling support
- [ ] Distributed document storage
- [ ] Backup and recovery
- [ ] Document versioning

### User Experience
- [ ] Web UI dashboard
- [ ] REST API for programmatic access
- [ ] WebSocket support for streaming
- [ ] Multi-user support with roles
- [ ] Document sharing and permissions
- [ ] Full-text search UI with filters

### Advanced Input
- [ ] Image text extraction (OCR)
- [ ] Audio transcription
- [ ] Video content indexing
- [ ] Structured data (databases)
- [ ] Source code indexing and search

### Knowledge Management
- [ ] Document organization (folders, tags)
- [ ] Automatic summarization
- [ ] Document relationships and linking
- [ ] Knowledge graph generation
- [ ] Duplicate detection

**Estimated Timeline:** H2 2025+

---

## Phase 4 🌟 Long-term Vision

**Enterprise & Ecosystem**

### Enterprise Features
- [ ] Fine-tuning on private data
- [ ] Custom model training
- [ ] Access control and audit logs
- [ ] SAML/OAuth authentication
- [ ] Data encryption at rest
- [ ] Compliance (GDPR, HIPAA, SOC2)

### Ecosystem
- [ ] Plugin system for custom components
- [ ] Pre-built integrations (Slack, Teams, Discord)
- [ ] Export/import formats
- [ ] Community plugin marketplace
- [ ] Documentation for extension developers

### Deployment
- [ ] Docker/Kubernetes deployment
- [ ] Cloud deployment templates (AWS, GCP, Azure)
- [ ] Edge deployment support
- [ ] Container registry for models
- [ ] Infrastructure-as-code examples

### Analytics & Insights
- [ ] Usage analytics
- [ ] Query success/failure tracking
- [ ] Model performance monitoring
- [ ] Cost tracking (if cloud-based)
- [ ] Recommendations engine

---

## Feature Request Process

Have a feature idea? Follow these steps:

1. **Check existing issues** — Is it already requested?
2. **Open GitHub Issue** — Describe your idea with:
   - Clear title and description
   - Use case and value
   - Proposed implementation (optional)
   - Label: `enhancement`

3. **Community Discussion** — Share your thoughts
4. **Prioritization** — Team evaluates and prioritizes
5. **Implementation** — Contribute or wait for team

---

## Priority Matrix

| Category | Phase | Priority | Impact |
|----------|-------|----------|--------|
| JSON output | 2 | High | Enables automation |
| PDF support | 2 | Medium | Broader document types |
| Vector search | 3 | High | Better semantic search |
| Multi-model | 3 | Medium | More LLM options |
| Web UI | 3 | Medium | Better UX |
| REST API | 3 | High | Programmatic access |
| PostgreSQL | 3 | Medium | Scalability |
| Fine-tuning | 4 | Low | Advanced use case |

---

## Known Limitations

**Phase 1 Constraints:**
- Single-user only
- SQLite doesn't scale to 100k+ documents efficiently
- Paragraph chunking loses some context
- FTS5 search quality depends on query format
- Synchronous API (blocks on LLM response)
- No streaming responses

**Phase 2 Will Address:**
- Search quality improvements
- Input format flexibility
- Better performance

**Phase 3 Will Address:**
- Scalability
- Advanced AI features
- Multi-model support

---

## Migration Path

Upgrading between phases:

### Phase 1 → Phase 2
- Database schema compatible
- Configuration compatible (new options added)
- No data migration needed
- All existing documents work as-is

### Phase 2 → Phase 3
- Can add vector embeddings without FTS5 removal
- Can switch to PostgreSQL with migration script
- All Phase 2 features work in Phase 3

---

## Contributing to Roadmap

See [Contributing Guide](guide.md) for:
- How to submit feature requests
- How to contribute implementations
- Code of conduct and expectations

---

## Timeline Estimates

| Phase | Duration | Target |
|-------|----------|--------|
| Phase 1 | ✅ Complete | Oct 2024 |
| Phase 2 | ~8 weeks | Q1 2025 |
| Phase 3 | ~12 weeks | H2 2025 |
| Phase 4 | Ongoing | 2026+ |

*Estimates are rough and subject to change based on community demand and contributor availability.*

---

## Questions?

- Have an idea? Open a GitHub issue with `enhancement` label
- Want to help? See [Contributing Guide](guide.md)
- Curious about a feature? Discuss in GitHub Discussions

Let's build the future of local AI together! 🚀
