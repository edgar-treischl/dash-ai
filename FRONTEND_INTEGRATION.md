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

