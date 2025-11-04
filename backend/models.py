"""Models for API"""

from pydantic import BaseModel, Field
from typing import Annotated, Optional


class ChatRequest(BaseModel):
    query: Annotated[str, "Mensaje del usuario para el modelo"] = Field(
        ...,
        description="The user's message to send to the chatbot",
        example="¿Qué es la inteligencia artificial?",
    )
    id: Annotated[str, "Identificador para acceder a la sesión del chatbot"] = Field(
        ...,
        description="Unique session identifier for the chatbot conversation",
        example="user-session-123",
    )
    asignatura: Optional[str] = Field(
        None, 
        description="Asignatura (subject) to bind to the agent state",
        example="IV",)

    class Config:
        json_schema_extra = {
            "example": {
                "query": "¿Cómo funciona el aprendizaje automático?",
                "id": "session-abc-123",
                "asignatura": "Guía docente de Trabajo Fin de Grado (Ingeniería Informática) (2971197)"
            }
        }


class MessageResponse(BaseModel):
    message: str = Field(
        ...,
        description="Response message from the API",
        example="Hello World",
    )

    class Config:
        json_schema_extra = {
            "example": {"message": "Hello World"}
        }


class ScrapeRequest(BaseModel):
    """Request body for scraping and indexing a `guia_docente`.

    html_content: the raw HTML of the guia
    url: optional original URL
    subject_override: optional field to force the subject value used as unique key
    """

    html_content: Annotated[str, "HTML content of the guia"] = Field(
        ..., description="Raw HTML content of the guia (string)"
    )
    url: Optional[str] = Field(None, description="Optional original URL for the guia")
    subject_override: Optional[str] = Field(
        None, description="If provided, will be used as the subject key stored in DB"
    )


class ScrapeResponse(BaseModel):
    status: str = Field(..., description="ok or error")
    subject: Optional[str] = Field(None, description="Subject/key used to index the document")
    upserted_id: Optional[str] = Field(
        None, description="Upserted id returned by MongoDB (if any)"
    )
    detail: Optional[dict] = Field(None, description="Detailed result from the upsert operation")


class SubjectItem(BaseModel):
    subject: str = Field(..., description="Unique subject identifier (asignatura)")
    metadata: Optional[dict] = Field(None, description="Optional metadata for the subject")


class SubjectsListResponse(BaseModel):
    subjects: list[SubjectItem]
