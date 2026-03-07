"""Pydantic models for the Math service."""

from pydantic import BaseModel


class HealthCheckResponse(BaseModel):
    """Health check response model."""

    status: str
    mongo_connected: bool = False
    ollama_connected: bool = False
    rag_service_connected: bool = False
    message: str = ""


class FAQ(BaseModel):
    """FAQ model."""

    question: str
    answer: str
    subject: str
    cluster_size: int
    status: str


class FAQGenerateRequest(BaseModel):
    """Request model for generating FAQs."""

    subject: str | None = None
    min_cluster_size: int = 3


class FAQGenerateResponse(BaseModel):
    """Response model for FAQ generation."""

    status: str
    subject: str | None = None
    questions_analyzed: int = 0
    clusters_formed: int = 0
    faqs_generated: int = 0
    faqs: list[str] = []
