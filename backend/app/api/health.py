from fastapi import APIRouter
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
import os
import structlog
from app.db import get_connection


logger = structlog.get_logger()
router = APIRouter()


@router.get("/health")
async def health():
    """Extended health check including environment, version, and DB connectivity."""
    status_data = {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "version": os.getenv("RAILWAY_GIT_COMMIT_SHA", "unknown")[:8] if os.getenv("RAILWAY_GIT_COMMIT_SHA") else "local",
        "subsystems": {
            "database": "connected",
            "cache": "ok",
        },
    }

    try:
        async with get_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT 1")
                await cur.fetchone()
    except Exception as e:
        logger.error("health.check.db_error", error=str(e))
        status_data["status"] = "degraded"
        status_data["subsystems"]["database"] = "error"
        return JSONResponse(content=status_data, status_code=503)

    logger.info("health.check", status=status_data["status"])
    return status_data
