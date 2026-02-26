"""Pydantic models for the Math service."""

from pydantic import BaseModel


class HealthCheckResponse(BaseModel):
    """Health check response model."""

    status: str
    mongo_connected: bool = False
    ollama_connected: bool = False
    rag_service_connected: bool = False
    message: str = ""
