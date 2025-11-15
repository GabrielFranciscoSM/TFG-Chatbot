"""Models for the agent tools input"""

from enum import Enum

from pydantic import BaseModel, Field


class WebSearchInput(BaseModel):
    """Input for the Web search tool"""

    query: str = Field(description="The search query string")


# Models for the Subject Lookup tool


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
        description="The key identifying the subject data to retrieve (one of: objectives, contents, methodology, evaluation, bibliography)"
    )


class SubjectLookupInput(BaseModel):
    """Input model for looking up a guia by subject.

    asignatura: optional the subject name/identifier to find
    key: specific sub-key to extract from the guia document
    """

    asignatura: str | None = Field(
        None,
        description=(
            "The current subject (asignatura) for which to retrieve the guia document. If unknown, the tool will read it from the agent's injected state."
        ),
    )

    key: SubjectDataKey = Field(
        None,
        description=(
            "Specific sub-key to return (e.g., resultados_de_aprendizaje, "
            "bibliografía, evaluación.evaluación_ordinaria)."
        ),
    )


# Models for the RAG tool


class RagQueryInput(BaseModel):
    """Input model for querying the RAG service.

    The agent can pass a free-text `query` and optional filters like
    `asignatura` and `tipo_documento`. `top_k` can be used to limit
    number of results returned by the RAG service.
    """

    query: str = Field(..., description="Search query for the RAG service")
    asignatura: str | None = Field(None, description="Optional subject filter")
    tipo_documento: str | None = Field(
        None, description="Optional document type filter"
    )
    top_k: int | None = Field(None, description="Optional number of results to return")


class DocumentMetadata(BaseModel):
    """Metadata for a document to be indexed in the RAG service."""

    content: str = Field(..., description="Content of the document")
    tipo_documento: str = Field(
        ..., description="Type of the document (e.g., lecture notes, exam)"
    )
    asignatura: str = Field(..., description="Subject associated with the document")
    fecha: str = Field(..., description="Date of the document (YYYY-MM-DD)")
    tema: str | None = Field(None, description="Topic of the document")
    autor: str = Field(..., description="Author of the document")
    fuente: str | None = Field(None, description="Source of the document")
    idioma: str = Field(
        ..., description="Language of the document (e.g., 'es' for Spanish)"
    )
    chunk_id: int | None = Field(
        None, description="Chunk ID if the document is part of a larger text"
    )
    licencia: str | None = Field(None, description="License of the document")


# Models for the test generation tool


class Question(BaseModel):
    """Model representing a question."""

    question_text: str = Field(..., description="The text of the question")
    difficulty: str | None = Field(
        None, description="Difficulty level of the question (e.g., easy, medium, hard)"
    )


class Answer(BaseModel):
    """Model representing an answer to a question."""

    answer_text: str = Field(..., description="The text of the answer")
    is_correct: bool = Field(..., description="Whether the answer is correct")


class MultipleChoiceTest(BaseModel):
    """Model representing a multiple-choice test."""

    question: Question = Field(..., description="The question being asked")
    options: list[Answer] = Field(
        ..., description="The answer options for the question"
    )


class TestGenerationInput(BaseModel):
    """Input model for generating a multiple-choice test."""

    topic: str = Field(..., description="The topic about which to generate the test")
    num_questions: int = Field(..., description="Number of questions to generate")
    difficulty: str | None = Field(
        None,
        description="Desired difficulty level of the questions (e.g., easy, medium, hard)",
    )
