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




# Frontend Integration Guide

This guide explains how the Vite frontend connects to the dash-ai backend through the FastAPI API.

## Architecture Overview

```
Frontend (Vite + React)
         ↓
Client (TypeScript)
         ↓
FastAPI Server (Port 8000)
         ↓
Dash AI CLI
         ↓
Local LLM (Ollama)
```

## Components

### 1. Backend: FastAPI API (`src/dash_ai/api/`)

The FastAPI server provides HTTP endpoints that the frontend can call:

#### **Main App** (`main.py`)
- Initializes the FastAPI application
- Registers routes
- Provides `/health` endpoint for status checks

#### **Routes** (`routes.py`)
- **POST `/api/query`** — Accepts a question and returns the LLM response
  - Request: `{"question": "your question here"}`
  - Response: `{"answer": "...", "sources": [...], ...}`

#### **Schemas** (`schemas.py`)
- Pydantic models for request/response validation
- `QueryRequest` — Defines the question input structure

### 2. Frontend: Vite + React (`frontend/`)

The React application runs on port 5173 and communicates with the API.

#### **API Client** (`src/api/client.ts`)
- `askQuestion(question: string)` — Sends a question to the backend
- Handles network errors and timeouts
- Returns typed response data

#### **App Component** (`src/App.tsx`)
- Chat interface for asking questions
- Displays responses from the API
- Shows loading state and error handling
- Inspector panel for viewing raw API responses

### 3. Proxy Configuration (`vite.config.ts`)

The Vite development server proxies API requests to the backend:

```typescript
server: {
  proxy: {
    "/api": {
      target: "http://localhost:8000",
      changeOrigin: true,
    },
  },
},
```

This allows the frontend to call `/api/query` during development without CORS issues.

## Running the Application

### Prerequisites

1. **Python Environment**
   ```bash
   # Install dependencies
   uv sync
   ```

2. **Node.js/npm**
   ```bash
   cd frontend
   npm install
   ```

3. **Ollama**
   ```bash
   # Start Ollama service
   ollama serve
   ```

### Quick Start

Run both services with one command:

```bash
./run-dev.sh
```

This will:
1. Start the FastAPI backend on `http://localhost:8000`
2. Start the Vite frontend on `http://localhost:5173`
3. Show URLs for frontend, backend, and API docs

### Manual Startup

**Terminal 1 — Backend:**
```bash
uv run uvicorn dash_ai.api.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```

**Terminal 3 — Ollama:**
```bash
ollama serve
```

## How It Works

### Flow Diagram

1. **User submits a question** in the React UI
2. **Frontend calls** `/api/query` with the question
3. **Vite proxy** routes the request to `http://localhost:8000/api/query`
4. **FastAPI** receives the request and validates it
5. **API calls** the dash-ai CLI: `uv run dash-ai chat --json "question"`
6. **CLI** processes the question through the RAG pipeline
7. **CLI** returns JSON with the answer
8. **FastAPI** returns this to the frontend
9. **Frontend** displays the answer and raw response

### Request/Response Example

**Request:**
```typescript
const response = await askQuestion("What is Python?");
```

**HTTP Call:**
```
POST http://localhost:8000/api/query
Content-Type: application/json

{
  "question": "What is Python?"
}
```

**Response:**
```json
{
  "answer": "Python is a high-level programming language...",
  "sources": ["docs/python-intro.md"],
  "confidence": 0.95,
  ...
}
```

## Environment Configuration

### Frontend Environment (`frontend/.env`)

```env
# API URL for production builds
VITE_API_URL=http://localhost:8000
```

During development, requests are proxied through Vite. For production, set `VITE_API_URL` to your backend URL.

### Backend Configuration

The backend inherits configuration from the main dash-ai application:
- Ollama settings from `config/settings.yaml`
- Knowledge base path from environment or config
- CLI command used to run the RAG pipeline

## Testing the Integration

### Using curl (Test Backend Only)

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is AI?"}'
```

### Using the Frontend

1. Open `http://localhost:5173`
2. Type a question in the chat input
3. Click "Send question"
4. View the answer and raw JSON response

### Health Check

```bash
curl http://localhost:8000/health
# Response: {"status":"ok","service":"dash-ai-api"}
```

### API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI).

## Production Deployment

### Building the Frontend

```bash
cd frontend
npm run build
```

This creates optimized static files in `frontend/dist/`.

### Running in Production

1. **Build the frontend**
   ```bash
   cd frontend && npm run build
   ```

2. **Serve static files with backend** (optional)
   - Copy `frontend/dist/` contents to a static directory
   - Configure FastAPI to serve them with `StaticFiles`

3. **Run the backend**
   ```bash
   uvicorn dash_ai.api.main:app --host 0.0.0.0 --port 8000
   ```

4. **Update `VITE_API_URL`** to point to your production API URL

## Troubleshooting

### "Connection refused" on the frontend

- ✓ Check that the FastAPI backend is running on port 8000
- ✓ Verify with: `curl http://localhost:8000/health`
- ✓ Check firewall settings if running on different machines

### API returns 502 or 504 errors

- ✓ Ensure Ollama is running: `ollama serve`
- ✓ Check that the `dash-ai` CLI is installed: `uv run dash-ai --help`
- ✓ Check backend logs for detailed error messages

### Frontend doesn't update after code changes

- ✓ Vite has hot module replacement enabled by default
- ✓ If it doesn't work, restart: `npm run dev`
- ✓ Clear browser cache: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows/Linux)

### CORS errors

- ✓ During development, requests are proxied through Vite (no CORS needed)
- ✓ For production, ensure the backend sends proper CORS headers

## Next Steps

- **Add authentication** to protect the API
- **Implement WebSockets** for streaming responses
- **Add file upload** to ingest new documents
- **Build API response types** with shared TypeScript types
- **Add response caching** to the frontend
- **Deploy** to production environment

## Extending the API

### Adding New Endpoints

1. Create a route function in `routes.py`:
   ```python
   @router.get("/documents")
   def list_documents():
       # Implementation
       return {"documents": [...]}
   ```

2. Add the schema in `schemas.py` if needed

3. The frontend can immediately call it via:
   ```typescript
   const docs = await fetch("/api/documents").then(r => r.json());
   ```

### Updating Response Types

Keep the TypeScript types in `frontend/src/api/client.ts` in sync with Python response structures. Consider using code generation tools like `openapi-generator` or `pydantic-to-typescript` to automate this.

