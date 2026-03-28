from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging
import os
from datetime import datetime
from backend.app.api.paddles import router as paddles_router
from backend.app.api.chat import router as chat_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("FastAPI startup — initializing...")
    # Could initialize DB pool, cache, etc. here
    yield
    # Shutdown
    logger.info("FastAPI shutdown — cleaning up...")
    # Close DB pool, cache, etc. here


app = FastAPI(title="PickleIQ", version="0.1.0", lifespan=lifespan)

# Include routers
app.include_router(paddles_router)
app.include_router(chat_router)


@app.get("/health")
async def health():
    """Production health check endpoint with environment and version info"""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "version": os.getenv("RAILWAY_GIT_COMMIT_SHA", "unknown")[:8] if os.getenv("RAILWAY_GIT_COMMIT_SHA") else "local"
    }
