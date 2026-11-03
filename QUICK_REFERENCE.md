# 🎯 Frontend-Backend Integration Quick Reference

## Start Here

```bash
./run-dev.sh
```

Then open: **http://localhost:5173**

---

## What's Running?

| Service | URL | Port |
|---------|-----|------|
| Frontend | http://localhost:5173 | 5173 |
| Backend API | http://localhost:8000 | 8000 |
| API Docs | http://localhost:8000/docs | 8000 |

---

## Commands

| Command | Purpose |
|---------|---------|
| `./run-dev.sh` | Start backend + frontend |
| `./test-integration.sh` | Verify backend ready |
| `uv run uvicorn dash_ai.api.main:app --reload` | Start API only |
| `cd frontend && npm run dev` | Start frontend only |
| `npm run build` | Build frontend for production |

---

## API Endpoints

### Ask a Question
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Python?"}'
```

### Check Health
```bash
curl http://localhost:8000/health
```

---

## File Structure

```
dash-ai/
├── src/dash_ai/api/
│   ├── main.py          ← FastAPI app + CORS
│   ├── routes.py        ← /api/query endpoint
│   ├── schemas.py       ← Pydantic models
│   └── __init__.py      ← Exports app
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── client.ts    ← API client
│   │   ├── App.tsx          ← UI component
│   │   └── main.tsx
│   ├── vite.config.ts       ← API proxy config
│   └── package.json
├── run-dev.sh           ← Start both services
├── test-integration.sh  ← Verify connection
└── QUICKSTART.md        ← Setup guide
```

---

## Error Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | ✓ Got answer |
| 422 | Bad request | Check question is not empty |
| 500 | Server error | Check Ollama is running |
| 502 | Bad gateway | Check CLI works: `uv run dash-ai --help` |
| 504 | Timeout | Question took too long, try simpler one |

---

## Troubleshooting

**Can't connect to API?**
- Check backend is running: `curl http://localhost:8000/health`
- Check Ollama is running: `ollama serve`

**Frontend won't load?**
- Check Node modules: `cd frontend && npm install`
- Kill port 5173: `lsof -i :5173` and note the PID, then `kill <PID>`

**API returns 502?**
- Check CLI works: `uv run dash-ai --help`
- Check knowledge base exists: `ls data/knowledge/`

---

## Docs

- 📖 **QUICKSTART.md** — 1-minute setup
- 📚 **FRONTEND_INTEGRATION.md** — Full guide
- 📋 **INTEGRATION_SUMMARY.md** — What was done
- 🔗 **http://localhost:8000/docs** — Interactive API docs

---

## Environment

**Backend** (`src/dash_ai/api/`)
- Port: 8000
- Auto-reload: ✓ (development)
- CORS: ✓ (enabled)

**Frontend** (`frontend/`)
- Port: 5173
- Proxy: /api → http://localhost:8000
- Hot reload: ✓

---

## Deploy

**Build frontend:**
```bash
cd frontend && npm run build
```

**Output:** `frontend/dist/` (ready to deploy)

**Run backend:** (separate from frontend)
```bash
uvicorn dash_ai.api.main:app --host 0.0.0.0 --port 8000
```

Set `VITE_API_URL` to your production API URL.

---

## Next Steps

- 🎨 Customize UI in `frontend/src/App.tsx`
- 🔌 Add endpoints in `src/dash_ai/api/routes.py`
- 🚀 Deploy frontend and backend separately
- 🔐 Add authentication to API
- 💾 Implement response caching

