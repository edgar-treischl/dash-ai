
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import router

app = FastAPI(
    title="Dash AI API",
    description="HTTP interface for the local LLM/RAG application",
    version="0.1.0",
)

# Configure CORS for frontend development and deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health", tags=["system"])
def health():
    return {
        "status": "ok",
        "service": "dash-ai-api",
    }
