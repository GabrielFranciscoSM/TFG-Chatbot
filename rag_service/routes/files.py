"""File-related endpoints: list, get info, load, upload."""

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


@router.get(
    "/files",
    tags=["Files"],
    summary="List files",
    description="Lists all available files in the documents directory, with optional filtering by subject (asignatura) and document type (tipo_documento).",
    response_model=FileListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_files(asignatura: str | None = None, tipo_documento: str | None = None):
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
    try:
        metadata_dict = json.loads(metadata)
        upload_metadata = UploadFileMetadata(**metadata_dict)
        file_extension = file.filename.split(".")[-1].lower()
        if file_extension not in ["txt", "pdf", "docx", "md", "markdown"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type: {file_extension}. Supported: txt, pdf, docx, md",
            )
        file_content = await file.read()
        file_loader = get_file_loader()
        saved_path = file_loader.save_uploaded_file(
            file_content=file_content,
            filename=file.filename,
            asignatura=upload_metadata.asignatura,
            tipo_documento=upload_metadata.tipo_documento,
        )
        logger.info(f"File saved: {saved_path}")
        indexed_count = 0
        if upload_metadata.auto_index:
            doc_metadata = DocumentMetadata(
                filename=file.filename,
                asignatura=upload_metadata.asignatura,
                tipo_documento=upload_metadata.tipo_documento,
                fecha=upload_metadata.fecha,
                tema=upload_metadata.tema,
                autor=upload_metadata.autor,
                fuente=upload_metadata.fuente,
                idioma=upload_metadata.idioma,
                licencia=upload_metadata.licencia,
            )
            document = file_loader.load_file(file.filename, doc_metadata)
            vector_store = get_vector_store()
            indexed_count = vector_store.index_documents([document])
            logger.info(f"Document indexed: {indexed_count} chunks")
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
