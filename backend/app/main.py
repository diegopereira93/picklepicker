from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging
from backend.app.api.paddles import router as paddles_router

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

# Include paddles router
app.include_router(paddles_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
