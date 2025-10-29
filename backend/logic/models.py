"""Models for the agent tools input"""

from pydantic import BaseModel, Field
from enum import Enum
from typing import Annotated
from typing import Optional
from langgraph.prebuilt import InjectedState
from langchain.tools import ToolRuntime

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
    # Use final JSON keys (Spanish) as enum values so agent can ask for them directly.
    OBJECTIVES = "resultados_de_aprendizaje"
    CONTENTS = "programa_de_contenidos_teóricos_y_prácticos"
    METHODOLOGY = "metodología_docente"
    EVALUATION = "evaluación"
    BIBLIOGRAPHY = "bibliografía"

    PREREQUISITES = "prerrequisitos_o_recomendaciones"
    BRIEF_DESCRIPTION = "breve_descripción_de_contenidos"
    COMPETENCES = "competencias"
    STAFF = "profesorado_y_tutorias"
    LINKS = "enlaces_recomendados"
    SOFTWARE = "software_libre"

    # Nested fields represented with dot notation
    BIBLIO_FUNDAMENTAL = "bibliografía.bibliografía_fundamental"
    BIBLIO_COMPLEMENTARY = "bibliografía.bibliografía_complementaria"
    EVALUACION_ORDINARIA = "evaluación.evaluación_ordinaria"
    EVALUACION_EXTRAORDINARIA = "evaluación.evaluación_extraordinaria"
    EVALUACION_UNICA_FINAL = "evaluación.evaluación_única_final"


class GetSubjectDataInput(BaseModel):
    """Input for the Get Subject Data tool"""
    key: SubjectDataKey = Field(
        description='The key identifying the subject data to retrieve (one of: objectives, contents, methodology, evaluation, bibliography)'
    )


class SubjectLookupInput(BaseModel):
    """Input model for looking up a guia by subject.

    subject: the subject name/identifier to find
    key: optional specific sub-key to extract from the guia document
    """
    # 'subject' is intentionally NOT part of the tool schema. The agent should
    # provide the asignatura via its injected state. Only the optional `key`
    # parameter is exposed to the tool.
    # NOTE: if the tool returns "No asignatura provided in agent state" or
    # otherwise appears not to find a subject, ensure the agent's state includes
    # the `asignatura` field (InjectedState("asignatura")) or pass the asignatura
    # to the agent via the API (for example, in the /chat request body).
    key: SubjectDataKey = Field(
        None,
        description=(
            "Optional specific sub-key to return (e.g., resultados_de_aprendizaje, "
            "bibliografía, evaluación.evaluación_ordinaria). The tool relies on the "
            "agent's injected state 'asignatura' to know which subject to query."
        ),
    )

    asignatura: Optional[str] = Field(
        None,
        description=(
            "The current subject (asignatura) for which to retrieve the guia document. If unknown, the tool will read it from the agent's injected state."
        ),
    )


class RagQueryInput(BaseModel):
    """Input model for querying the RAG service.

    The agent can pass a free-text `query` and optional filters like
    `asignatura` and `tipo_documento`. `top_k` can be used to limit
    number of results returned by the RAG service.
    """
    query: str = Field(..., description="Search query for the RAG service")
    asignatura: Optional[str] = Field(None, description="Optional subject filter")
    tipo_documento: Optional[str] = Field(None, description="Optional document type filter")
    top_k: Optional[int] = Field(None, description="Optional number of results to return")


class DocumentMetadata(BaseModel):
    """Metadata for a document to be indexed in the RAG service."""
    content: str = Field(..., description="Content of the document")
    tipo_documento: str = Field(..., description="Type of the document (e.g., lecture notes, exam)")
    asignatura: str = Field(..., description="Subject associated with the document")
    fecha: str = Field(..., description="Date of the document (YYYY-MM-DD)")
    tema: Optional[str] = Field(None, description="Topic of the document")
    autor: str = Field(..., description="Author of the document")
    fuente: Optional[str] = Field(None, description="Source of the document")
    idioma: str = Field(..., description="Language of the document (e.g., 'es' for Spanish)")
    chunk_id: Optional[int] = Field(None, description="Chunk ID if the document is part of a larger text")
    licencia: Optional[str] = Field(None, description="License of the document")