# 🎯 Frontend Integration Guide

## Overview

Your **Vite React frontend** is now fully integrated with the **FastAPI backend**, which connects to the **dash-ai CLI** and **Ollama LLM**.

### What You Get

✅ **React UI** for asking questions (Port 5173)  
✅ **FastAPI Backend** that orchestrates the RAG pipeline (Port 8000)  
✅ **Type-safe Communication** between frontend and backend  
✅ **Error Handling** and proper status codes  
✅ **CORS Support** for cross-origin requests  
✅ **Hot Reload** during development  
✅ **Swagger Documentation** at `/docs`

---

## 🚀 Getting Started (30 seconds)

### 1. Ensure Dependencies Are Installed
```bash
uv sync
cd frontend && npm install && cd ..
```

### 2. Start All Services
```bash
make dev
```

### 3. Open Browser
```
http://localhost:5173
```

That's it! You now have:
- Frontend: http://localhost:5173 (Vite + React)
- Backend: http://localhost:8000 (FastAPI)
- API Docs: http://localhost:8000/docs (Swagger)

---

## 📋 How It Works

### User Flow

1. **User types a question** in the React UI
2. **Frontend sends POST** to `/api/query` with the question
3. **Vite dev server proxies** the request to `http://localhost:8000`
4. **FastAPI validates** the request with Pydantic
5. **Backend calls** `uv run dash-ai chat --json "question"`
6. **CLI processes** the question through the RAG pipeline using Ollama
7. **Response returned** as JSON through the chain
8. **Frontend displays** the answer and raw response

### Data Flow Diagram

```
React Component
    ↓
askQuestion("What is X?")
    ↓
fetch POST /api/query
    ↓
Vite Proxy (localhost:5173 → localhost:8000)
    ↓
FastAPI (validate, call CLI)
    ↓
CLI: dash-ai chat "What is X?"
    ↓
RAG Pipeline + Ollama LLM
    ↓
JSON Response
    ↓
React State Update
    ↓
UI Re-renders
```

---

## 🛠️ Available Commands

### Development
| Command | Purpose | Port |
|---------|---------|------|
| `make dev` | Start backend + frontend | 5173, 8000 |
| `make api` | Start only FastAPI backend | 8000 |
| `make frontend` | Start only Vite frontend | 5173 |
| `make test-integration` | Verify connection works | - |

### Utility
| Command | Purpose |
|---------|---------|
| `make start` | Start Ollama service |
| `make start-bg` | Start Ollama in background |
| `make stop-bg` | Stop background Ollama |
| `make build-frontend` | Build for production |
| `make clean` | Clean build artifacts |

### Testing
| Command | Purpose |
|---------|---------|
| `make test` | Run pytest suite |
| `make ask QUESTION="..."` | Ask via CLI (for testing) |

---

## 📁 Project Structure

### Backend
```
src/dash_ai/api/
├── __init__.py       # Exports FastAPI app
├── main.py          # FastAPI app setup + CORS
├── routes.py        # Endpoints (/api/query)
└── schemas.py       # Pydantic models (QueryRequest)
```

### Frontend
```
frontend/src/
├── api/
│   └── client.ts    # API client + types
├── App.tsx          # Main chat component
├── App.css          # Styles
└── main.tsx         # React entry point
```

### Configuration
```
pyproject.toml       # Python dependencies (FastAPI, uvicorn)
frontend/package.json # Node.js dependencies (React, Vite)
frontend/vite.config.ts  # Vite proxy config
Makefile             # Development commands
```

---

## 🔌 API Reference

### POST /api/query
Ask a question to the RAG pipeline.

**Request:**
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is machine learning?"}'
```

**Response:**
```json
{
  "answer": "Machine learning is a subset of artificial intelligence...",
  "sources": ["document.md"],
  "confidence": 0.95
}
```

**Error Responses:**
- `422` — Bad request (empty question)
- `500` — Server error (Ollama not running)
- `502` — Bad gateway (CLI failed)
- `504` — Timeout (request too long)

### GET /health
Check if the API is running.

**Request:**
```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "ok",
  "service": "dash-ai-api"
}
```

### GET /docs
Interactive API documentation (Swagger UI).

Visit: http://localhost:8000/docs

---

## 🧪 Testing

### Test 1: Check Backend is Running
```bash
curl http://localhost:8000/health
```

Expected: `{"status":"ok","service":"dash-ai-api"}`

### Test 2: Run Integration Tests
```bash
./test-integration.sh
```

This verifies:
- Health endpoint responds
- API docs are available
- Input validation works
- CORS headers are set
- Request format is correct

### Test 3: Test in Browser
1. Open http://localhost:5173
2. Type a question
3. Submit
4. View the response + raw JSON in the inspector panel

### Test 4: Direct API Call
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "test"}'
```

Expected: Either a full response (200) or an error (500/502/504)

---

## 🎨 Customizing the UI

### Edit the React Component
File: `frontend/src/App.tsx`

```typescript
// Change the heading
<h1>My Custom AI Assistant</h1>

// Add new input fields
// Modify the layout
// Change colors in App.css
```

The component will hot-reload on save.

### Customize Styles
File: `frontend/src/App.css`

Modify colors, fonts, spacing, etc. Changes appear instantly.

### Add New API Calls
File: `frontend/src/api/client.ts`

```typescript
export async function getDocuments() {
  const result = await fetch(`${API_BASE_URL}/api/documents`);
  return result.json();
}
```

Then use in App.tsx:
```typescript
const docs = await getDocuments();
```

---

## 🔧 Adding Backend Endpoints

### 1. Define the Route
File: `src/dash_ai/api/routes.py`

```python
@router.get("/documents")
def list_documents():
    return {
        "documents": ["doc1.md", "doc2.md"]
    }
```

### 2. (Optional) Define the Schema
File: `src/dash_ai/api/schemas.py`

```python
class DocumentResponse(BaseModel):
    documents: list[str]
```

### 3. Use in Frontend
File: `frontend/src/api/client.ts`

```typescript
export interface Document {
  name: string;
}

export async function listDocuments(): Promise<Document[]> {
  const result = await fetch(`${API_BASE_URL}/api/documents`);
  return result.json();
}
```

### 4. Use in Component
File: `frontend/src/App.tsx`

```typescript
const docs = await listDocuments();
```

---

## 🚀 Production Deployment

### Build Frontend
```bash
make build-frontend
```

Output: `frontend/dist/` (static files ready to deploy)

### Deploy Frontend
- Upload `frontend/dist/` to your static hosting (Vercel, Netlify, S3, etc.)
- Or serve with FastAPI using `StaticFiles` middleware

### Deploy Backend
```bash
uvicorn dash_ai.api.main:app --host 0.0.0.0 --port 8000
```

### Update API URL
In `frontend/.env`:
```
VITE_API_URL=https://your-api.com
```

Then rebuild frontend:
```bash
npm run build
```

---

## 🐛 Troubleshooting

### Issue: "Connection refused"
**Cause:** Backend not running  
**Fix:** Start with `make api` (in a separate terminal)

### Issue: Frontend can't reach API
**Cause:** Vite proxy misconfigured  
**Fix:** Check `frontend/vite.config.ts` has proxy to `http://localhost:8000`

### Issue: API returns 502 error
**Cause:** CLI not working or Ollama not running  
**Fix:**  
1. Check Ollama: `ollama serve`
2. Check CLI: `uv run dash-ai --help`
3. Check logs in terminal where backend is running

### Issue: Changes not showing
**Cause:** Hot reload not working  
**Fix:** 
1. Hard refresh browser: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows/Linux)
2. Restart dev server: `make frontend`

### Issue: Port already in use
**Cause:** Process already running on that port  
**Fix:**
```bash
# Find process using port 5173
lsof -i :5173

# Kill it (note the PID from above)
kill <PID>
```

---

## 📚 Documentation

| File | Purpose |
|------|---------|
| `QUICKSTART.md` | 1-minute setup guide |
| `QUICK_REFERENCE.md` | Command reference card |
| `FRONTEND_INTEGRATION.md` | Detailed architecture |
| `INTEGRATION_SUMMARY.md` | What was integrated |
| `INTEGRATION_STATUS.md` | Current status |
| `FRONTEND_GUIDE.md` | This file |

---

## ✨ Next Steps

- 🎨 Customize the UI in `App.tsx`
- 🔌 Add new API endpoints in `routes.py`
- 📊 Add response caching
- 🔐 Add authentication to API
- 💬 Implement WebSocket for streaming responses
- 🚀 Deploy to production

---

## 💡 Tips

1. **Use Swagger UI** at http://localhost:8000/docs to test endpoints
2. **Check terminal logs** for error details
3. **Use browser DevTools** to inspect network requests
4. **Keep frontend & backend in separate terminals** for `make api` and `make frontend`
5. **Always start Ollama first** before the backend

---

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review relevant documentation
3. Check backend logs (terminal where `make api` runs)
4. Check frontend logs (terminal where `make frontend` runs)

**Ready to build amazing AI applications!** 🚀

