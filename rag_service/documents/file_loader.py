"""File loading utilities for RAG service."""

import os
from pathlib import Path
from typing import List, Optional
import logging

from rag_service.config import settings
from rag_service.models import Document, DocumentMetadata

logger = logging.getLogger(__name__)


class FileLoader:
    """Service for loading documents from files."""
    
    def __init__(self, documents_path: Optional[str] = None):
        """
        Initialize file loader.
        
        Args:
            documents_path: Path to documents directory (default: from settings)
        """
        self.documents_path = Path(documents_path or settings.documents_path)
        
        # Create directory if it doesn't exist
        self.documents_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"FileLoader initialized with path: {self.documents_path}")
    
    def load_text_file(self, filepath: Path, metadata: DocumentMetadata) -> Document:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            doc_id = filepath.stem  # Use filename without extension as ID
            
            return Document(
                content=content,
                metadata=metadata,
                doc_id=doc_id
            )
        except Exception as e:
            logger.error(f"Error loading text file {filepath}: {e}")
            raise
    
    def load_pdf_file(self, filepath: Path, metadata: DocumentMetadata) -> Document:
        try:
            from pypdf import PdfReader
            
            reader = PdfReader(filepath)
            content_parts = []
            
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    content_parts.append(text)
            
            content = "\n\n".join(content_parts)
            doc_id = filepath.stem
            
            logger.info(f"Loaded PDF with {len(reader.pages)} pages")
            
            return Document(
                content=content,
                metadata=metadata,
                doc_id=doc_id
            )
        except ImportError:
            logger.error("pypdf not installed. Install with: pip install pypdf")
            raise
        except Exception as e:
            logger.error(f"Error loading PDF file {filepath}: {e}")
            raise
    
    def load_markdown_file(self, filepath: Path, metadata: DocumentMetadata) -> Document:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            doc_id = filepath.stem  # Use filename without extension as ID
            
            logger.info(f"Loaded Markdown file: {filepath.name}")
            
            return Document(
                content=content,
                metadata=metadata,
                doc_id=doc_id
            )
        except Exception as e:
            logger.error(f"Error loading Markdown file {filepath}: {e}")
            raise
    
    def _get_organized_path(self, asignatura: str, tipo_documento: str, filename: str) -> Path:
        asignatura_norm = asignatura.lower().replace(" ", "-").replace("_", "-")
        tipo_documento_norm = tipo_documento.lower().replace(" ", "-").replace("_", "-")
        
        subject_dir = self.documents_path / asignatura_norm / tipo_documento_norm
        subject_dir.mkdir(parents=True, exist_ok=True)
        
        return subject_dir / filename
    
    def load_file(self, filename: str, metadata: DocumentMetadata) -> Document:
        if metadata.asignatura and metadata.tipo_documento:
            filepath = self._get_organized_path(
                metadata.asignatura, 
                metadata.tipo_documento, 
                filename
            )
            
            if not filepath.exists():
                filepath = self.documents_path / filename
        else:
            filepath = self.documents_path / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        extension = filepath.suffix.lower()
        
        if extension == '.txt':
            return self.load_text_file(filepath, metadata)
        elif extension == '.pdf':
            return self.load_pdf_file(filepath, metadata)
        elif extension in ['.md', '.markdown']:
            return self.load_markdown_file(filepath, metadata)
        else:
            raise ValueError(f"Unsupported file type: {extension}")
    
    def save_uploaded_file(
        self, 
        file_content: bytes, 
        filename: str, 
        asignatura: str, 
        tipo_documento: str
    ) -> Path:
        try:
            filepath = self._get_organized_path(asignatura, tipo_documento, filename)
            with open(filepath, 'wb') as f:
                f.write(file_content)
            
            logger.info(f"File saved: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error saving file: {e}")
            raise


# Global file loader instance
_file_loader: FileLoader | None = None

def get_file_loader() -> FileLoader:
    global _file_loader
    if _file_loader is None:
        _file_loader = FileLoader()
    return _file_loader
