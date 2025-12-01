"""Models for API"""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    query: Annotated[str, "Mensaje del usuario para el modelo"] = Field(
        ...,
        description="The user's message to send to the chatbot",
        json_schema_extra={"example": "¿Qué es la inteligencia artificial?"},
    )
    id: Annotated[str, "Identificador para acceder a la sesión del chatbot"] = Field(
        ...,
        description="Unique session identifier for the chatbot conversation",
        json_schema_extra={"example": "user-session-123"},
    )
    asignatura: str | None = Field(
        None,
        description="Asignatura (subject) to bind to the agent state",
        json_schema_extra={"example": "IV"},
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "query": "¿Cómo funciona el aprendizaje automático?",
                "id": "session-abc-123",
                "asignatura": "Guía docente de Trabajo Fin de Grado (Ingeniería Informática) (2971197)",
            }
        }
    )


class MessageResponse(BaseModel):
    message: str = Field(
        ...,
        description="Response message from the API",
        json_schema_extra={"example": "Hello World"},
    )

    model_config = ConfigDict(json_schema_extra={"example": {"message": "Hello World"}})


class ScrapeRequest(BaseModel):
    """Request body for scraping and indexing a `guia_docente`.

    html_content: the raw HTML of the guia
    url: optional original URL
    subject_override: optional field to force the subject value used as unique key
    """

    html_content: Annotated[str, "HTML content of the guia"] = Field(
        ..., description="Raw HTML content of the guia (string)"
    )
    url: str | None = Field(None, description="Optional original URL for the guia")
    subject_override: str | None = Field(
        None, description="If provided, will be used as the subject key stored in DB"
    )


class ScrapeResponse(BaseModel):
    status: str = Field(..., description="ok or error")
    subject: str | None = Field(
        None, description="Subject/key used to index the document"
    )
    upserted_id: str | None = Field(
        None, description="Upserted id returned by MongoDB (if any)"
    )
    detail: dict | None = Field(
        None, description="Detailed result from the upsert operation"
    )


class SubjectItem(BaseModel):
    subject: str = Field(..., description="Unique subject identifier (asignatura)")
    metadata: dict | None = Field(None, description="Optional metadata for the subject")


class SubjectsListResponse(BaseModel):
    subjects: list[SubjectItem]


# === Test Session Models ===


class ResumeRequest(BaseModel):
    """Request to resume an interrupted test session."""

    id: str = Field(
        ...,
        description="Thread ID of the interrupted conversation",
        json_schema_extra={"example": "user-session-123"},
    )
    user_response: str = Field(
        ...,
        description="User's answer to the current question",
        json_schema_extra={
            "example": "Un bucle for se utiliza para iterar sobre secuencias"
        },
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "session-abc-123",
                "user_response": "Un bucle for se utiliza para iterar sobre secuencias de elementos",
            }
        }
    )


class InterruptInfo(BaseModel):
    """Information about an interrupted test session."""

    action: str = Field(
        ...,
        description="Type of action that caused the interrupt",
        json_schema_extra={"example": "answer_question"},
    )
    question_num: int = Field(
        ...,
        description="Current question number (1-indexed)",
        json_schema_extra={"example": 1},
    )
    total_questions: int = Field(
        ...,
        description="Total number of questions in the test",
        json_schema_extra={"example": 5},
    )
    question_text: str = Field(
        ...,
        description="Text of the current question",
        json_schema_extra={"example": "¿Qué es un bucle for en Python?"},
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "action": "answer_question",
                "question_num": 1,
                "total_questions": 5,
                "question_text": "¿Qué es un bucle for en Python?",
            }
        }
    )


class ChatMessage(BaseModel):
    """A single message in the conversation."""

    type: str = Field(..., description="Message type: 'ai', 'human', 'tool', 'system'")
    content: str = Field(..., description="The message content")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"type": "ai", "content": "Hello! How can I help you?"}
        }
    )


class ChatResponse(BaseModel):
    """Response for chat endpoints - returns only the last assistant message."""

    message: ChatMessage | None = Field(
        None, description="The assistant's response message"
    )
    interrupted: bool = Field(
        default=False,
        description="Whether the conversation was interrupted (waiting for user input)",
    )
    interrupt_info: InterruptInfo | None = Field(
        None, description="Information about the interrupt, if interrupted=True"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": {
                    "type": "ai",
                    "content": "📝 Pregunta 1/5\n\n¿Qué es un bucle for en Python?",
                },
                "interrupted": True,
                "interrupt_info": {
                    "action": "answer_question",
                    "question_num": 1,
                    "total_questions": 5,
                    "question_text": "¿Qué es un bucle for en Python?",
                },
            }
        }
    )


class HistoryResponse(BaseModel):
    """Response for history endpoint - returns all messages."""

    messages: list[ChatMessage] = Field(
        default_factory=list, description="All messages in the conversation"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "messages": [
                    {"type": "human", "content": "¿Qué es Docker?"},
                    {
                        "type": "ai",
                        "content": "Docker es una plataforma de contenedores...",
                    },
                ]
            }
        }
    )
