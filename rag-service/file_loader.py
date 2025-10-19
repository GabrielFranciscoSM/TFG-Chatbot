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
        """
        Load a text file and create a Document.
        
        Args:
            filepath: Path to the text file
            metadata: Metadata for the document
            
        Returns:
            Document object
        """
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
        """
        Load a PDF file and create a Document.
        
        Args:
            filepath: Path to the PDF file
            metadata: Metadata for the document
            
        Returns:
            Document object
        """
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
        """
        Load a Markdown file and create a Document.
        
        Args:
            filepath: Path to the Markdown file
            metadata: Metadata for the document
            
        Returns:
            Document object
        """
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
        """
        Get the organized path for a document following the structure:
        documents/{asignatura}/{tipo_documento}/{filename}
        
        Args:
            asignatura: Subject name (e.g., "logica-difusa")
            tipo_documento: Document type (e.g., "apuntes", "ejercicios")
            filename: File name
            
        Returns:
            Full path to the file
        """
        # Normalize names (lowercase, replace spaces with hyphens)
        asignatura_norm = asignatura.lower().replace(" ", "-").replace("_", "-")
        tipo_documento_norm = tipo_documento.lower().replace(" ", "-").replace("_", "-")
        
        # Create directory structure if it doesn't exist
        subject_dir = self.documents_path / asignatura_norm / tipo_documento_norm
        subject_dir.mkdir(parents=True, exist_ok=True)
        
        return subject_dir / filename
    
    def load_file(self, filename: str, metadata: DocumentMetadata) -> Document:
        """
        Load a file based on its extension.
        Supports both flat structure and organized structure (asignatura/tipo_documento/filename).
        
        Args:
            filename: Name of the file (can include path like "asignatura/tipo_documento/file.pdf")
            metadata: Metadata for the document
            
        Returns:
            Document object
        """
        # Try organized path first (using metadata)
        if metadata.asignatura and metadata.tipo_documento:
            filepath = self._get_organized_path(
                metadata.asignatura, 
                metadata.tipo_documento, 
                filename
            )
            
            # If file doesn't exist in organized path, try flat structure
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
        """
        Save an uploaded file to the organized directory structure.
        
        Args:
            file_content: Binary content of the file
            filename: Name of the file
            asignatura: Subject name
            tipo_documento: Document type
            
        Returns:
            Path where the file was saved
        """
        try:
            # Get organized path
            filepath = self._get_organized_path(asignatura, tipo_documento, filename)
            
            # Write file
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
    """
    Get or create the global file loader instance.
    
    Returns:
        FileLoader instance
    """
    global _file_loader
    if _file_loader is None:
        _file_loader = FileLoader()
    return _file_loader
