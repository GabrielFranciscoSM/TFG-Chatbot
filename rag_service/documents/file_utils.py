"""File listing and info utilities for RAG service."""

from pathlib import Path
from typing import List, Optional
import logging
from ..config import settings

logger = logging.getLogger(__name__)

documents_path = Path(settings.documents_path)

def list_files(asignatura: Optional[str] = None, tipo_documento: Optional[str] = None) -> List[str]:
    try:
        files = []
        if asignatura and tipo_documento:
            asignatura_norm = asignatura.lower().replace(" ", "-").replace("_", "-")
            tipo_documento_norm = tipo_documento.lower().replace(" ", "-").replace("_", "-")
            target_dir = documents_path / asignatura_norm / tipo_documento_norm
            if target_dir.exists():
                for item in target_dir.iterdir():
                    if item.is_file():
                        files.append(f"{asignatura_norm}/{tipo_documento_norm}/{item.name}")
        elif asignatura:
            asignatura_norm = asignatura.lower().replace(" ", "-").replace("_", "-")
            subject_dir = documents_path / asignatura_norm
            if subject_dir.exists():
                for tipo_dir in subject_dir.iterdir():
                    if tipo_dir.is_dir():
                        for item in tipo_dir.iterdir():
                            if item.is_file():
                                files.append(f"{asignatura_norm}/{tipo_dir.name}/{item.name}")
        else:
            for item in documents_path.rglob("*"):
                if item.is_file():
                    rel_path = item.relative_to(documents_path)
                    files.append(str(rel_path))
        logger.info(f"Found {len(files)} files")
        return sorted(files)
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        raise

def list_subjects() -> List[str]:
    try:
        subjects = []
        for item in documents_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                subjects.append(item.name)
        logger.info(f"Found {len(subjects)} subjects")
        return sorted(subjects)
    except Exception as e:
        logger.error(f"Error listing subjects: {e}")
        raise

def list_document_types(asignatura: str) -> List[str]:
    try:
        asignatura_norm = asignatura.lower().replace(" ", "-").replace("_", "-")
        subject_dir = documents_path / asignatura_norm
        if not subject_dir.exists():
            return []
        doc_types = []
        for item in subject_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
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
