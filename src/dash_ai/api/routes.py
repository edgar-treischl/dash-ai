
import json
import subprocess

from fastapi import APIRouter, HTTPException

from .schemas import QueryRequest

router = APIRouter(prefix="/api", tags=["query"])

CLI_TIMEOUT = 300


@router.post("/query")
def query(request: QueryRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=422,
            detail="Question cannot be empty",
        )

    try:
        result = subprocess.run(
            [
                "uv",
                "run",
                "dash-ai",
                "chat",
                "--json",
                question,
            ],
            capture_output=True,
            text=True,
            timeout=CLI_TIMEOUT,
            check=False,
        )

    except subprocess.TimeoutExpired:
        raise HTTPException(
            status_code=504,
            detail="LLM request timed out",
        )

    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail="Could not find the uv executable",
        )

    if result.returncode != 0:
        raise HTTPException(
            status_code=502,
            detail={
                "message": "RAG pipeline execution failed",
                "stderr": result.stderr[-2000:],
            },
        )

    try:
        response = json.loads(result.stdout)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=502,
            detail="CLI did not return valid JSON",
        )

    return response
