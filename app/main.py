# --- Standard Python Libraries ---
import asyncio
import json
import logging
from contextlib import asynccontextmanager

# --- Third-Party Libraries ---
import aio_pika
from fastapi import FastAPI
from pydantic import ValidationError

# --- Local Application Imports ---
from .config import settings
from .logging_config import setup_logging
from .schemas import NotificationRequest, StatusUpdateRequest, NotificationStatus

# --- Globals ---
RABBITMQ_CONNECTION = None

app = FastAPI(
    title="Email Notification Service",
    lifespan=lifespan
)

@app.get("/health", status_code=200, tags=["Status"])
def health_check():
    """
    Endpoint to check if the service is alive.
    """
    return {"status": "ok", "service": "email-service"}