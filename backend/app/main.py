from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
import logging
import os
import time
import uuid
import asyncio
from datetime import datetime
from app.api.paddles import router as paddles_router
from app.api.chat import router as chat_router
from app.api.health import router as health_router
from app.api.price_history import router as price_history_router
from app.api.embeddings import router as embeddings_router
from app.routers.affiliate import router as affiliate_router
from app.logging_config import configure_logging
from app.middleware.alerts import alerter
from app.db import get_pool, close_pool
import structlog

logger = structlog.get_logger()


# Initialize logging based on environment
environment = os.getenv("ENVIRONMENT", "development")
configure_logging(environment)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("FastAPI startup — initializing...")
    await get_pool()  # Initialize DB connection pool
    yield
    # Shutdown
    logger.info("FastAPI shutdown — cleaning up...")
    await close_pool()  # Close DB connection pool


app = FastAPI(title="PickleIQ", version="0.1.0", lifespan=lifespan)

# Include routers
app.include_router(paddles_router, prefix="/api/v1")
app.include_router(chat_router)
app.include_router(health_router)
app.include_router(price_history_router)
app.include_router(embeddings_router)
app.include_router(affiliate_router, tags=["affiliate"])


# HTTP request/response logging middleware
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start = time.time()

    logger.info(
        "http.request",
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        query=str(request.url.query) if request.url.query else None
    )

    response = await call_next(request)
    duration = time.time() - start

    logger.info(
        "http.response",
        request_id=request_id,
        status=response.status_code,
        duration_ms=round(duration * 1000, 2)
    )

    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    from fastapi.responses import JSONResponse
    logger.error("unhandled.exception", error=str(exc), path=request.url.path)

    # Send alert for errors (fire-and-forget)
    asyncio.create_task(
        alerter.send_alert(
            severity="ERROR",
            title="API Exception",
            details=str(exc)[:200],
            context={"path": request.url.path}
        )
    )

    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )
