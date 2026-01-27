#!/usr/bin/env python3
"""
Palace Dashboard - 24/7 Monitoring & Control
=============================================

Real-time view of all butlers, knowledge library, cloud jobs, automation.

Run locally:
    uvicorn main:app --reload --port 8080

Deploy to Cloud Run:
    ./deploy.sh
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import os

# Import routers
from routers import butlers, knowledge, cloud_jobs, health, automation, files

# Paths
DASHBOARD_DIR = Path(__file__).parent
STATIC_DIR = DASHBOARD_DIR / "static"

# Get project root (dashboard is at PROJECT_elements/dashboard/)
PROJECT_ROOT = DASHBOARD_DIR.parent

# Environment
GCS_BUCKET = os.getenv("GCS_BUCKET", "elements-archive-2026")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Create app
app = FastAPI(
    title="Palace Dashboard API",
    description="24/7 monitoring and control for PROJECT_elements",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS (allow web access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: restrict to dashboard domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(butlers.router, prefix="/api/butlers", tags=["Butlers"])
app.include_router(knowledge.router, prefix="/api/knowledge", tags=["Knowledge"])
app.include_router(cloud_jobs.router, prefix="/api/cloud/jobs", tags=["Cloud Jobs"])
app.include_router(health.router, prefix="/api/health", tags=["Health"])
app.include_router(automation.router, prefix="/api/automation", tags=["Automation"])
app.include_router(files.router, prefix="/api/files", tags=["Files"])

# Serve static frontend
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def dashboard_ui():
    """Serve main dashboard HTML."""
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health_check():
    """Health check endpoint for Cloud Run."""
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/api/meta/info")
def dashboard_info():
    """Dashboard metadata."""
    return {
        "dashboard_version": "1.0.0",
        "api_version": "1.0",
        "project_root": str(PROJECT_ROOT),
        "gcs_bucket": GCS_BUCKET,
        "endpoints": {
            "total": 20,
            "categories": ["butlers", "knowledge", "cloud", "automation", "health", "files"]
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
