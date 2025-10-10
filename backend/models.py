"""Models for API"""

from pydantic import BaseModel, Field
from typing import Annotated

class ChatRequest(BaseModel):
    query: Annotated[str, "Mensaje del usuario para el modelo"] = Field(
        ..., 
        description="The user's message to send to the chatbot",
        example="¿Qué es la inteligencia artificial?"
    )
    id: Annotated[str, "Identificador para acceder a la sesión del chatbot"] = Field(
        ..., 
        description="Unique session identifier for the chatbot conversation",
        example="user-session-123"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "¿Cómo funciona el aprendizaje automático?",
                "id": "session-abc-123"
            }
        }


class MessageResponse(BaseModel):
    message: str = Field(
        ..., 
        description="Response message from the API",
        example="Hello World"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Hello World"
            }
        }