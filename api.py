"""FastAPI Backend Entry Point for Air Pollution Imputation Research.

Minimal API entry point prepared for future ML pipeline and frontend integration.
Model inference, SLM encoding, and diffusion pipelines are not implemented yet.
"""

from typing import Any, Dict
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI(
    title="Air Pollution Imputation API",
    description="Backend service for Air Pollution Missing Data Imputation research",
    version="0.1.0",
)

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root() -> Dict[str, Any]:
    """Root endpoint returning project identity and status."""
    return {
        "status": "ok",
        "project": "Air Pollution Missing Data Imputation",
        "stage": "foundation/scaffolding",
    }


@app.get("/api/health")
def health_check() -> Dict[str, Any]:
    """Health check endpoint for frontend and service monitoring."""
    return {
        "status": "healthy",
        "stage": "scaffolding",
        "message": "Air Pollution Imputation backend service is operational.",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)
