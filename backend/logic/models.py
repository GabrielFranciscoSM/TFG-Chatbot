"""Models for the agent tools input"""

from pydantic import BaseModel, Field
from enum import Enum
from typing import Annotated

class WebSearchInput(BaseModel):
    """Input for the Web search tool"""
    query: str = Field(description="The search query string")

class CalculatorInput(BaseModel):
    """Input for the Calculator tool"""
    expression: str = Field(
        description='A mathematical expression to evaluate (e.g., "2 + 2", "5 * 3")'
    )

class SubjectDataKey(str, Enum):
    """Allowed keys for subject data retrieval."""
    OBJECTIVES = "objectives"
    CONTENTS = "contents"
    METHODOLOGY = "methodology"
    EVALUATION = "evaluation"
    BIBLIOGRAPHY = "bibliography"


class GetSubjectDataInput(BaseModel):
    """Input for the Get Subject Data tool"""
    key: SubjectDataKey = Field(
        description='The key identifying the subject data to retrieve (one of: objectives, contents, methodology, evaluation, bibliography)'
    )