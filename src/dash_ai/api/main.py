
from fastapi import FastAPI

from .routes import router

app = FastAPI(
    title="Dash AI API",
    description="HTTP interface for the local LLM/RAG application",
    version="0.1.0",
)

app.include_router(router)


@app.get("/health", tags=["system"])
def health():
    return {
        "status": "ok",
        "service": "dash-ai-api",
    }
