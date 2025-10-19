"""Subject-related endpoints: list subjects and document types."""

from fastapi import APIRouter, HTTPException, status
import logging
from rag_service.models import SubjectListResponse, DocumentTypesResponse
from rag_service.file_utils import list_subjects, list_document_types

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get(
    "/subjects",
    tags=["Subjects"],
    summary="List subjects",
    description="Lists all available subjects (asignaturas) found in the documents directory.",
    response_model=SubjectListResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "List of subject names and total count"},
        500: {"description": "Failed to list subjects"}
    }
)
async def list_subjects():
    try:
        subjects = list_subjects()
        return SubjectListResponse(
            subjects=subjects,
            total_subjects=len(subjects),
        )
    except Exception as e:
        logger.error(f"Error listing subjects: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list subjects: {str(e)}"
        )

@router.get(
    "/subjects/{asignatura}/types",
    tags=["Subjects"],
    summary="List document types for subject",
    description="Lists all document types for a given subject (asignatura).",
    response_model=DocumentTypesResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "List of document types and total count"},
        500: {"description": "Failed to list document types"}
    }
)
async def list_document_types(asignatura: str):
    try:
        doc_types = list_document_types(asignatura)
        return DocumentTypesResponse(
            asignatura=asignatura,
            document_types=doc_types,
            total_types=len(doc_types),
        )
    except Exception as e:
        logger.error(f"Error listing document types: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list document types: {str(e)}"
        )
