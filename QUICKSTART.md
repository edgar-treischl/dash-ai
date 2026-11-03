# Quick Start: Frontend + Backend Integration

## One-Minute Setup

### 1. Install Dependencies

```bash
# Install Python packages
uv sync

# Install Node.js packages
cd frontend && npm install && cd ..
```

### 2. Start Services

```bash
# Start Ollama (in a separate terminal)
ollama serve

# Start both frontend and backend
./run-dev.sh
```

### 3. Open Browser

Visit: **http://localhost:5173**

Ask a question and get answers from your local LLM!

---

## What's Running?

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | http://localhost:5173 | React UI for asking questions |
| **Backend API** | http://localhost:8000 | FastAPI server with `/api/query` endpoint |
| **API Docs** | http://localhost:8000/docs | Swagger UI for exploring endpoints |
| **Ollama** | http://localhost:11434 | Local language model runtime |

---

## Testing Without the UI

**Test the API directly:**

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is machine learning?"}'
```

**Expected response:**
```json
{
  "answer": "Machine learning is a subset of artificial intelligence...",
  "sources": ["file.md"],
  ...
}
```

---

## Troubleshooting

**Backend won't start?**
- ✓ Check Ollama is running: `ollama serve`
- ✓ Check port 8000 is available: `lsof -i :8000`

**Frontend won't load?**
- ✓ Check Node.js is installed: `node --version`
- ✓ Reinstall packages: `cd frontend && npm install`

**API returns an error?**
- ✓ Check backend logs: See console output from `./run-dev.sh`
- ✓ Verify CLI works: `uv run dash-ai --help`

---

## Next Steps

- 📖 Read [`FRONTEND_INTEGRATION.md`](./FRONTEND_INTEGRATION.md) for full architecture details
- 🛠️ Customize the UI in `frontend/src/App.tsx`
- 🔌 Add more API endpoints in `src/dash_ai/api/routes.py`
- 🚀 Deploy with production configuration

