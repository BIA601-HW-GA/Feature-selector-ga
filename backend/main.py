from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from .api import api_router
from .config import logger, PROJECT_ROOT, ALLOWED_ORIGINS
from fastapi.middleware.cors import CORSMiddleware 

app = FastAPI(
    title="Genetic Feature Selection API",
    description="Feature selection using Genetic Algorithms with comparison to traditional methods",
    version="1.0.0"
)

# Security: Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

logger.info(f"CORS enabled for origins: {ALLOWED_ORIGINS}")

# Include API routes
app.include_router(api_router)

# Serve frontend
frontend_dir = PROJECT_ROOT / "frontend"
if not frontend_dir.exists():
    raise RuntimeError(f"Directory '{frontend_dir}' does not exist")
app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")

# Serve outputs folder
app.mount("/outputs", StaticFiles(directory=str(PROJECT_ROOT / "outputs"), html=True), name="outputs")

@app.on_event("startup")
def startup_event():
    logger.info("Application started successfully")

# For debugging purposes, you can keep the old main_improved.py as a backup, but it's no longer needed.