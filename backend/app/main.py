"""
FastAPI application entry point.

Registers all routers, configures CORS, and starts the SQS background
worker on startup. The app is served by Uvicorn on port 8000 and proxied
through Nginx which forwards /api/* to this process.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes import auth, files, share, notifications
from app.workers.share_worker import start_worker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Worker thread handle — kept alive for the application lifetime
_worker_thread = None
_stop_event = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage startup and shutdown tasks.

    On startup: launches the SQS background worker thread.
    On shutdown: signals the worker to stop cleanly.
    """
    global _worker_thread, _stop_event
    logger.info("Starting SQS share worker...")
    _worker_thread, _stop_event = start_worker()

    yield  # Application runs here

    logger.info("Stopping SQS share worker...")
    _stop_event.set()
    _worker_thread.join(timeout=10)


app = FastAPI(
    title="CloudShare API",
    description="Cloud-based file sharing system powered by AWS S3, DynamoDB, SQS, SNS, and Cognito.",
    version="1.0.0",
    lifespan=lifespan,
)

# Allow requests from the Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register route modules
app.include_router(auth.router)
app.include_router(files.router)
app.include_router(share.router)
app.include_router(notifications.router)


@app.get("/api/health", tags=["health"])
async def health_check():
    """Public health check endpoint.

    Returns a simple status response to confirm the API is running.
    No authentication required — used by load balancers and monitoring.
    """
    return {"status": "ok", "service": "CloudShare API", "version": "1.0.0"}
