# Documentation Index

Welcome to Dash-AI documentation! Here you'll find everything you need to install, use, and extend Dash-AI.

## Start Here

**New to Dash-AI?** Start with one of these:
- **[User Guide](user_guide.md)** — Installation, quick start, all CLI commands (← Start here!)
- **[FAQ](faq.md)** — 25+ common questions answered
- **[Troubleshooting](troubleshooting.md)** — Solutions to common problems

## User Documentation (Phase 2)

### 📖 [User Guide](user_guide.md)
Complete guide for using Dash-AI:
- Installation steps (macOS, Linux, Windows/WSL)
- Quick start in 5 minutes
- All CLI commands with examples (`ingest`, `ask`, `chat`, `list`, `delete`)
- Interactive mode walkthrough
- Configuration options
- JSON output format
- Advanced usage patterns
- Troubleshooting quick reference

**Read this if:** You're installing Dash-AI or learning how to use it.

### 🆘 [Troubleshooting Guide](troubleshooting.md)
Solutions to common issues:
- Connection problems (Ollama not responding)
- Model issues (not found, pull access denied)
- Search & retrieval issues (empty results)
- Performance problems (slow responses)
- Storage issues (database locked, out of memory)
- Encoding and format issues
- Configuration problems
- Command-specific solutions
- Advanced debugging techniques

**Read this if:** Something isn't working as expected.

### 💡 [Examples](examples.md)
Practical usage patterns and real-world scenarios:
- Ingesting personal notes
- Asking questions about code
- Building a technical reference
- Interactive chatbot workflows
- Batch processing with JSON
- Python integration
- Documentation analysis
- Team knowledge bases
- Advanced patterns and automations

**Read this if:** You want inspiration for how to use Dash-AI.

### ❓ [FAQ](faq.md)
Frequently asked questions organized by topic:
- General questions (what is Dash-AI, how it differs from ChatGPT)
- Installation & setup (prerequisites, Windows support)
- Usage questions (file formats, configuration)
- Model & performance (which models, hardware requirements)
- Data & privacy (is my data private, how to back up)
- Integration & customization (Python library, web apps)
- Advanced questions (real-time applications, fine-tuning)
- Troubleshooting questions (common errors)
- Performance & optimization
- Licensing & legal

**Read this if:** You have a specific question not answered elsewhere.

---

## Developer & Architecture Documentation

### 🏗️ Architecture Guide
Located in `user_guide/architecture/`:
- [Architecture Overview](../user_guide/architecture/overview.md) — System design, components, data flow
- [Module Details](../user_guide/architecture/modules.md) — Code organization, class reference

**Read this if:** You're contributing to Dash-AI or want to understand the internals.

### 📚 Contributing Guide
Located in `user_guide/contributing/`:
- [Contributing Guide](../user_guide/contributing/guide.md) — Development setup, workflow, conventions
- [Testing Guide](../user_guide/contributing/testing.md) — How to write and run tests

**Read this if:** You want to contribute code or improvements.

### 📊 Phase Reports
Located in `user_guide/implementation/`:
- [Phase 1 Summary](../user_guide/implementation/phase-1-summary.md) — What was built
- [Phase 1 Complete](../user_guide/implementation/phase-1-complete.md) — Detailed implementation report

**Read this if:** You want to understand what has been implemented.

---

## Reference Documentation

### ⚙️ API Reference
Located in `user_guide/api/`:
- [CLI Reference](../user_guide/api/cli.md) — Complete command reference with examples
- [Python API](../user_guide/api/python.md) — Using Dash-AI as a Python library

**Read this if:** You need detailed information about specific commands or APIs.

### 🚀 Quick Guides
Located in `user_guide/guides/`:
- [Quick Start](../user_guide/guides/quickstart.md) — Get running in 5 minutes
- [Configuration Reference](../user_guide/guides/configuration.md) — All configuration options
- [Ollama Guide](../user_guide/guides/ollama.md) — Setting up and using Ollama
- [Roadmap](../user_guide/guides/roadmap.md) — Future development plans

**Read this if:** You want a focused guide on a specific topic.

### 📈 Performance Documentation
- [Performance Guide](performance.md) — Performance metrics and optimization tips
- [Profiling Results](profiling_results.md) — Detailed profiling analysis

**Read this if:** You want to optimize performance or understand bottlenecks.

---

## Navigation by Use Case

### "I'm new to Dash-AI"
1. Read: [User Guide](user_guide.md) → Installation & Quick Start sections
2. Try: The quick start examples
3. Reference: [FAQ](faq.md) for questions
4. Explore: [Examples](examples.md) for inspiration

### "I want to use it for my project"
1. Install: Follow [User Guide](user_guide.md)
2. Learn: Read relevant sections from [Examples](examples.md)
3. Reference: Check [CLI Reference](../user_guide/api/cli.md) for commands
4. Debug: Use [Troubleshooting Guide](troubleshooting.md) if issues arise

### "I'm having a problem"
1. Check: [Troubleshooting Guide](troubleshooting.md)
2. Search: [FAQ](faq.md) for similar questions
3. Read: Relevant section from [User Guide](user_guide.md)
4. Report: [GitHub Issues](https://github.com/edgar-treischl/dash-ai/issues) if unresolved

### "I want to contribute"
1. Start: [Contributing Guide](../user_guide/contributing/guide.md)
2. Code: Follow [Architecture Guide](../user_guide/architecture/overview.md)
3. Test: Learn from [Testing Guide](../user_guide/contributing/testing.md)
4. PR: Submit your changes to GitHub

### "I want to understand the system"
1. Big picture: [Architecture Overview](../user_guide/architecture/overview.md)
2. Components: [Module Details](../user_guide/architecture/modules.md)
3. Implementation: [Phase 1 Complete Report](../user_guide/implementation/phase-1-complete.md)
4. Extend: [Architecture Overview](../user_guide/architecture/overview.md#future-extensibility)

---

## Documentation Statistics

| Category | Files | Content | Purpose |
|----------|-------|---------|---------|
| **User Docs** | 4 | ~2,600 lines | Getting started, using, troubleshooting |
| **API Docs** | 2 | ~19,000 lines | Command and function reference |
| **Architecture** | 2 | ~15,000 lines | System design, code organization |
| **Contributing** | 2 | ~20,000 lines | Development workflow, testing |
| **Guides** | 4 | ~23,000 lines | Quickstart, configuration, roadmap |
| **Reports** | 2 | ~17,000 lines | Phase 1 implementation details |
| **Performance** | 2 | ~5,500 lines | Performance metrics, profiling |
| **Total** | 18+ | ~102,000 words | Complete documentation |

---

## Document Organization

```
docs/
├── README.md (this file)
├── user_guide.md (← New! Phase 2)
├── troubleshooting.md (← New! Phase 2)
├── examples.md (← New! Phase 2)
├── faq.md (← New! Phase 2)
├── performance.md (Phase 2)
├── profiling_results.md (Phase 2)
│
├── user_guide/
│   ├── CONTENTS.md
│   ├── STRUCTURE.txt
│   ├── api/
│   │   ├── cli.md
│   │   └── python.md
│   ├── architecture/
│   │   ├── overview.md
│   │   └── modules.md
│   ├── guides/
│   │   ├── quickstart.md
│   │   ├── configuration.md
│   │   ├── ollama.md
│   │   └── roadmap.md
│   ├── contributing/
│   │   ├── guide.md
│   │   └── testing.md
│   └── implementation/
│       ├── phase-1-summary.md
│       └── phase-1-complete.md
```

---

## Reading Paths

### Path 1: Quick Learning (20 minutes)
1. User Guide → Installation & Quick Start (5 min)
2. FAQ → 5 key questions (5 min)
3. Examples → One scenario (10 min)
**Result:** Ready to use Dash-AI

### Path 2: Comprehensive Understanding (2-3 hours)
1. User Guide → Full read (1 hour)
2. Architecture Overview → System design (30 min)
3. Examples → Browse several scenarios (30 min)
4. FAQ → Skim all questions (30 min)
**Result:** Expert user, understand how it works

### Path 3: Developer Deep Dive (4-5 hours)
1. Architecture Overview → System design (1 hour)
2. Module Details → Code organization (1 hour)
3. Contributing Guide → Development workflow (1 hour)
4. Testing Guide → How to write tests (1 hour)
5. Phase 1 Complete → Implementation details (30 min)
**Result:** Ready to contribute, understand internals

### Path 4: Troubleshooting (varies)
1. Troubleshooting Guide → Find your issue (10-20 min)
2. FAQ → Check related questions (5-10 min)
3. User Guide → Verify your usage (5-10 min)
**Result:** Issue resolved

---

## How to Navigate

- **Use Ctrl+F (Cmd+F on macOS)** to search within a document
- **Click links** to jump between sections
- **Table of Contents** at the top of each document
- **"Read this if:" sections** help you pick the right document
- **Cross-references** link related topics

---

## Document Versions

**Phase 2** (current)
- ✅ User Guide, Troubleshooting, Examples, FAQ (new!)
- ✅ Enhanced error handling, interactive mode, JSON output
- ✅ 90%+ test coverage, performance profiling
- ✅ Comprehensive documentation

**Phase 1** (completed)
- ✅ Basic CLI (ingest, ask, list, delete)
- ✅ Markdown ingestion, SQLite storage
- ✅ Full-text search, LLM integration (Ollama)
- ✅ ~80 tests, core architecture

**Future**
- Phase 3: PDF support, vector search, REST API
- Phase 4: Fine-tuning, plugins, cloud deployment

---

## Quick Links

- 🚀 **Get Started:** [User Guide](user_guide.md)
- ❓ **Questions:** [FAQ](faq.md)
- 🆘 **Problems:** [Troubleshooting](troubleshooting.md)
- 💡 **Ideas:** [Examples](examples.md)
- 🏗️ **Deep Dive:** [Architecture Overview](../user_guide/architecture/overview.md)
- 👨‍💻 **Contribute:** [Contributing Guide](../user_guide/contributing/guide.md)
- 🗺️ **What's Next:** [Roadmap](../user_guide/guides/roadmap.md)

---

## Feedback & Contributions

- Found an error in the docs? [Open an issue](https://github.com/edgar-treischl/dash-ai/issues)
- Have a suggestion? [Start a discussion](https://github.com/edgar-treischl/dash-ai/discussions)
- Want to improve docs? [Submit a PR](https://github.com/edgar-treischl/dash-ai/pulls)

See [Contributing Guide](../user_guide/contributing/guide.md) for details.

---

## Maintenance

**Last Updated:** October 31, 2024  
**Documentation Version:** Phase 2  
**Status:** Complete and up-to-date

Documentation is maintained alongside code changes. See contributing guide for details on keeping docs current.
