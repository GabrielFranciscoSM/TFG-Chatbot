"""
File-related endpoints for document management.

This module provides REST API endpoints for managing documents in the RAG service:
- List files with optional filtering by subject and document type
- Get metadata and information about specific files
- Load existing files and index them for semantic search
- Upload new files and optionally index them automatically

Examples:
    List all files:
        GET /files

    List files for a specific subject:
        GET /files?asignatura=ingenieria-informatica

    Upload and index a file:
        POST /upload
        Content-Type: multipart/form-data
        - file: <binary data>
        - metadata: {"asignatura": "iv", "tipo_documento": "teoria", "auto_index": true}
"""

import json
import logging

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from rag_service.documents.file_loader import get_file_loader
from rag_service.documents.file_utils import get_file_info as file_info
from rag_service.documents.file_utils import list_files as ls_files
from rag_service.embeddings.store import get_vector_store
from rag_service.models import (
    DocumentMetadata,
    FileListResponse,
    LoadFileRequest,
    LoadFileResponse,
    UploadFileMetadata,
)

logger = logging.getLogger(__name__)

router = APIRouter()


def _validate_file_extension(filename: str) -> str:
    """
    Validate that file has a supported extension.

    Args:
        filename: Name of the file to validate

    Returns:
        The file extension in lowercase

    Raises:
        HTTPException: If file extension is not supported
    """
    file_extension = filename.split(".")[-1].lower()
    supported_extensions = ["txt", "pdf", "docx", "md", "markdown"]

    if file_extension not in supported_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file_extension}. Supported: {', '.join(supported_extensions)}",
        )

    return file_extension


def _index_uploaded_document(
    file_loader,
    filename: str,
    metadata: UploadFileMetadata,
) -> int:
    """
    Index an uploaded document if auto_index is enabled.

    Args:
        file_loader: FileLoader instance
        filename: Name of the file to index
        metadata: Upload metadata containing indexing configuration

    Returns:
        Number of chunks indexed (0 if auto_index is False)
    """
    if not metadata.auto_index:
        return 0

    doc_metadata = DocumentMetadata(
        filename=filename,
        asignatura=metadata.asignatura,
        tipo_documento=metadata.tipo_documento,
        fecha=metadata.fecha,
        tema=metadata.tema,
        autor=metadata.autor,
        fuente=metadata.fuente,
        idioma=metadata.idioma,
        licencia=metadata.licencia,
    )

    document = file_loader.load_file(filename, doc_metadata)
    vector_store = get_vector_store()
    indexed_count = vector_store.index_documents([document])

    logger.info(f"Document indexed: {indexed_count} chunks")
    return indexed_count


@router.get(
    "/files",
    tags=["Files"],
    summary="List files",
    description="Lists all available files in the documents directory, with optional filtering by subject (asignatura) and document type (tipo_documento).",
    response_model=FileListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_files(asignatura: str | None = None, tipo_documento: str | None = None):
    """
    List all available files in the documents directory.

    Files are organized by subject (asignatura) and document type (tipo_documento).
    You can filter results by providing these parameters.

    Args:
        asignatura: Optional subject name to filter files (e.g., "ingenieria-informatica")
        tipo_documento: Optional document type to filter files (e.g., "teoria", "ejercicios")

    Returns:
        FileListResponse containing list of file paths and total count

    Raises:
        HTTPException: 500 if listing files fails

    Example:
        GET /files?asignatura=iv&tipo_documento=teoria
    """
    try:
        files = ls_files(asignatura, tipo_documento)
        return FileListResponse(
            files=files,
            total_files=len(files),
        )
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list files: {str(e)}",
        ) from e


@router.get(
    "/files/{filename:path}",
    tags=["Files"],
    summary="Get file information",
    status_code=status.HTTP_200_OK,
)
async def get_file_info(filename: str):
    """
    Get metadata and information about a specific file.

    Returns file size, extension, and modification time.

    Args:
        filename: Relative path to the file (e.g., "iv/teoria/tema1.pdf")

    Returns:
        Dictionary with file information: filename, size_bytes, size_kb, extension, modified

    Raises:
        HTTPException: 404 if file not found, 500 for other errors

    Example:
        GET /files/iv/teoria/tema1.pdf
    """
    try:
        return file_info(filename)
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Error getting file info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get file info: {str(e)}",
        ) from e


@router.post(
    "/load-file",
    tags=["Files"],
    summary="Load and index file",
    response_model=LoadFileResponse,
    status_code=status.HTTP_200_OK,
)
async def load_file(request: LoadFileRequest):
    """
    Load an existing file from the documents directory and index it for semantic search.

    This endpoint is useful for indexing files that were manually placed in the
    documents directory or uploaded without the auto_index option.

    Args:
        request: LoadFileRequest containing filename and document metadata

    Returns:
        LoadFileResponse with filename, doc_id, and number of chunks indexed

    Raises:
        HTTPException:
            - 404 if file not found
            - 400 for invalid file type
            - 500 for other errors

    Example:
        POST /load-file
        {
            "filename": "iv/teoria/tema1.pdf",
            "metadata": {
                "asignatura": "iv",
                "tipo_documento": "teoria",
                "tema": "Introducción"
            }
        }
    """
    try:
        file_loader = get_file_loader()
        vector_store = get_vector_store()
        document = file_loader.load_file(request.filename, request.metadata)
        indexed_count = vector_store.index_documents([document])
        return LoadFileResponse(
            filename=request.filename,
            doc_id=document.doc_id,
            indexed_count=indexed_count,
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
    except Exception as e:
        logger.error(f"Error loading file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load file: {str(e)}",
        ) from e


@router.post(
    "/upload",
    tags=["Files"],
    summary="Upload and index file",
    response_model=LoadFileResponse,
    status_code=status.HTTP_200_OK,
)
async def upload_file(file: UploadFile = File(...), metadata: str = Form(...)):
    """
    Upload a file and optionally index it for semantic search.

    Args:
        file: The file to upload
        metadata: JSON string containing upload metadata and indexing configuration

    Returns:
        LoadFileResponse with filename, doc_id, and number of indexed chunks

    Raises:
        HTTPException: If file type is unsupported, metadata is invalid, or upload fails
    """
    try:
        # Parse and validate metadata
        metadata_dict = json.loads(metadata)
        upload_metadata = UploadFileMetadata(**metadata_dict)

        # Validate file extension
        _validate_file_extension(file.filename)

        # Read and save file
        file_content = await file.read()
        file_loader = get_file_loader()
        saved_path = file_loader.save_uploaded_file(
            file_content=file_content,
            filename=file.filename,
            asignatura=upload_metadata.asignatura,
            tipo_documento=upload_metadata.tipo_documento,
        )
        logger.info(f"File saved: {saved_path}")

        # Index document if requested
        indexed_count = _index_uploaded_document(
            file_loader, file.filename, upload_metadata
        )

        return LoadFileResponse(
            filename=file.filename,
            doc_id=saved_path.stem,
            indexed_count=indexed_count,
        )
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid metadata JSON format",
        ) from e
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}",
        ) from e
