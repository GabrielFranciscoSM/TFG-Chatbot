"""File listing and info utilities for RAG service."""

import logging
from pathlib import Path

from rag_service.config import settings

logger = logging.getLogger(__name__)

documents_path = Path(settings.documents_path)


def _normalize_name(name: str) -> str:
    """Normalize subject/document type name to directory format."""
    return name.lower().replace(" ", "-").replace("_", "-")


def _list_files_in_dir(directory: Path, base_path: Path) -> list[str]:
    """
    List all files in a directory recursively.

    Args:
        directory: Directory to search for files
        base_path: Base path to calculate relative paths

    Returns:
        List of file paths relative to base_path
    """
    files = []
    for item in directory.rglob("*"):
        if item.is_file():
            rel_path = item.relative_to(base_path)
            files.append(str(rel_path))
    return files


def _list_files_by_subject_and_type(
    asignatura_norm: str, tipo_documento_norm: str
) -> list[str]:
    """List files for specific subject and document type."""
    target_dir = documents_path / asignatura_norm / tipo_documento_norm
    files = []
    if target_dir.exists():
        for item in target_dir.iterdir():
            if item.is_file():
                files.append(f"{asignatura_norm}/{tipo_documento_norm}/{item.name}")
    return files


def _list_files_by_subject(asignatura_norm: str) -> list[str]:
    """List all files for a specific subject across all document types."""
    subject_dir = documents_path / asignatura_norm
    files = []
    if subject_dir.exists():
        for tipo_dir in subject_dir.iterdir():
            if tipo_dir.is_dir():
                for item in tipo_dir.iterdir():
                    if item.is_file():
                        files.append(f"{asignatura_norm}/{tipo_dir.name}/{item.name}")
    return files


def list_files(
    asignatura: str | None = None, tipo_documento: str | None = None
) -> list[str]:
    """
    List files in the documents directory with optional filtering.

    Args:
        asignatura: Optional subject name to filter by
        tipo_documento: Optional document type to filter by

    Returns:
        Sorted list of file paths relative to documents directory

    Raises:
        Exception: If listing files fails
    """
    try:
        if asignatura and tipo_documento:
            # List files for specific subject and document type
            asignatura_norm = _normalize_name(asignatura)
            tipo_documento_norm = _normalize_name(tipo_documento)
            files = _list_files_by_subject_and_type(
                asignatura_norm, tipo_documento_norm
            )
        elif asignatura:
            # List all files for specific subject
            asignatura_norm = _normalize_name(asignatura)
            files = _list_files_by_subject(asignatura_norm)
        else:
            # List all files in documents directory
            files = _list_files_in_dir(documents_path, documents_path)

        logger.info(f"Found {len(files)} files")
        return sorted(files)
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        raise


def list_subjects() -> list[str]:
    try:
        subjects = []
        for item in documents_path.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                subjects.append(item.name)
        logger.info(f"Found {len(subjects)} subjects")
        return sorted(subjects)
    except Exception as e:
        logger.error(f"Error listing subjects: {e}")
        raise


def list_document_types(asignatura: str) -> list[str]:
    """
    List document types available for a specific subject.

    Args:
        asignatura: Subject name to get document types for

    Returns:
        Sorted list of document type names

    Raises:
        Exception: If listing document types fails
    """
    try:
        asignatura_norm = _normalize_name(asignatura)
        subject_dir = documents_path / asignatura_norm

        if not subject_dir.exists():
            return []

        doc_types = []
        for item in subject_dir.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                doc_types.append(item.name)

        logger.info(f"Found {len(doc_types)} document types for {asignatura}")
        return sorted(doc_types)
    except Exception as e:
        logger.error(f"Error listing document types: {e}")
        raise


def get_file_info(filename: str) -> dict:
    filepath = documents_path / filename
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    stat = filepath.stat()
    return {
        "filename": filename,
        "size_bytes": stat.st_size,
        "size_kb": round(stat.st_size / 1024, 2),
        "extension": filepath.suffix,
        "modified": stat.st_mtime,
    }
