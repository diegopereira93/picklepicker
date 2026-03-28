from fastapi import APIRouter
from datetime import datetime
import os
import structlog


logger = structlog.get_logger()
router = APIRouter()


@router.get("/health")
async def health():
    """Extended health check including environment and version info."""
    status_data = {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "version": os.getenv("RAILWAY_GIT_COMMIT_SHA", "unknown")[:8] if os.getenv("RAILWAY_GIT_COMMIT_SHA") else "local",
        "subsystems": {
            "database": "ok",  # Placeholder - actual check requires DB connection
            "cache": "ok"      # Placeholder - Redis optional
        }
    }

    logger.info("health.check", status=status_data["status"])
    return status_data
