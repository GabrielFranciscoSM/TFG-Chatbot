"""Models for the agent tools input"""

from pydantic import BaseModel, Field
from typing import Annotated

class WebSearchInput(BaseModel):
    """Input for the Web search tool"""
    query: str = Field(description="The search query string")

class CalculatorInput(BaseModel):
    """Input for the Calculator tool"""
    expresion: str = Field(
        description= 'A mathematical expression to evaluate (e.g., "2 + 2", "5 * 3")'
        )