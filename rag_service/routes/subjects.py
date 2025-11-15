"""Subject-related endpoints: list subjects and document types."""

import logging

from fastapi import APIRouter, HTTPException, status

from rag_service.documents.file_utils import list_document_types as ls_document_types
from rag_service.documents.file_utils import list_subjects as ls_subjects
from rag_service.models import DocumentTypesResponse, SubjectListResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/subjects",
    tags=["Subjects"],
    summary="List subjects",
    response_model=SubjectListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_subjects():
    try:
        subjects = ls_subjects()
        return SubjectListResponse(
            subjects=subjects,
            total_subjects=len(subjects),
        )
    except Exception as e:
        logger.error(f"Error listing subjects: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list subjects: {str(e)}",
        ) from e


@router.get(
    "/subjects/{asignatura}/types",
    tags=["Subjects"],
    summary="List document types for subject",
    response_model=DocumentTypesResponse,
    status_code=status.HTTP_200_OK,
)
async def list_document_types(asignatura: str):
    try:
        doc_types = ls_document_types(asignatura)
        return DocumentTypesResponse(
            asignatura=asignatura,
            document_types=doc_types,
            total_types=len(doc_types),
        )
    except Exception as e:
        logger.error(f"Error listing document types: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list document types: {str(e)}",
        ) from e
