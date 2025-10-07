from pydantic import BaseModel
from typing import Annotated

class ChatRequest(BaseModel):
    query:  Annotated[str,"Mensaje del usuario para el modelo"]
    id:     Annotated[str,"Identificador para acceder a la sesión del chatbot"]