"""Pydantic models for the Math service."""

from datetime import datetime

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


class TopicExtractRequest(BaseModel):
    """Request model for extracting topics."""

    subject: str
    vectorizer_type: str = "tfidf"
    k: int | None = None
    cost_function: str = "frobenius"


class ConceptNode(BaseModel):
    """A node in the concept map."""

    id: str
    group: str
    label: str


class ConceptLink(BaseModel):
    """A link in the concept map."""

    source: str
    target: str
    value: float


class ConceptMap(BaseModel):
    """A concept map containing nodes and links."""

    nodes: list[ConceptNode]
    links: list[ConceptLink]


class TopicDetails(BaseModel):
    """Details of an extracted topic."""

    cluster: int
    topic_name: str
    terms: list[str]
    weight: float


class TopicResult(BaseModel):
    """Response model for topic extraction."""

    status: str
    subject: str | None = None
    clusters_formed: int = 0
    topics: list[TopicDetails] = []
    concept_map: ConceptMap | None = None
    doc_topic_matrix: list[list[float]] | None = None
    created_at: datetime | None = None
    source_chunks: int = 0
    message: str | None = None
