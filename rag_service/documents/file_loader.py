"""
File loading utilities for the RAG service.

This module provides the FileLoader class that handles loading documents from
various file formats and organizing them in a structured directory hierarchy.

File Organization:
    documents/
    ├── asignatura-1/
    │   ├── tipo-documento-1/
    │   │   └── file1.pdf
    │   └── tipo-documento-2/
    │       └── file2.md
    └── asignatura-2/
        └── tipo-documento-1/
            └── file3.txt

Supported formats:
    - .txt: Plain text files
    - .pdf: PDF documents
    - .md, .markdown: Markdown files
    - .docx: Word documents (planned)

Example:
    loader = get_file_loader()

    # Load a file
    metadata = DocumentMetadata(
        filename="tema1.pdf",
        asignatura="iv",
        tipo_documento="teoria"
    )
    document = loader.load_file("iv/teoria/tema1.pdf", metadata)

    # Save uploaded file
    saved_path = loader.save_uploaded_file(
        file_content=bytes_data,
        filename="tema2.pdf",
        asignatura="iv",
        tipo_documento="ejercicios"
    )
"""

import logging
from pathlib import Path

from rag_service.config import settings
from rag_service.models import Document, DocumentMetadata

logger = logging.getLogger(__name__)


class FileLoader:
    """Service for loading documents from files."""

    def __init__(self, documents_path: str | None = None):
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
        Load a plain text file.

        Args:
            filepath: Path to the text file
            metadata: Document metadata

        Returns:
            Document object with file content and metadata

        Raises:
            Exception: If file reading fails
        """
        try:
            with open(filepath, encoding="utf-8") as f:
                content = f.read()

            doc_id = filepath.stem  # Use filename without extension as ID

            return Document(content=content, metadata=metadata, doc_id=doc_id)
        except Exception as e:
            logger.error(f"Error loading text file {filepath}: {e}")
            raise

    def load_pdf_file(self, filepath: Path, metadata: DocumentMetadata) -> Document:
        """
        Load a PDF file and extract text from all pages.

        Args:
            filepath: Path to the PDF file
            metadata: Document metadata

        Returns:
            Document object with extracted text and metadata

        Raises:
            ImportError: If pypdf is not installed
            Exception: If PDF reading fails
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

            return Document(content=content, metadata=metadata, doc_id=doc_id)
        except ImportError:
            logger.error("pypdf not installed. Install with: pip install pypdf")
            raise
        except Exception as e:
            logger.error(f"Error loading PDF file {filepath}: {e}")
            raise

    def load_markdown_file(
        self, filepath: Path, metadata: DocumentMetadata
    ) -> Document:
        """
        Load a Markdown file.

        Args:
            filepath: Path to the Markdown file
            metadata: Document metadata

        Returns:
            Document object with Markdown content and metadata

        Raises:
            Exception: If file reading fails
        """
        try:
            with open(filepath, encoding="utf-8") as f:
                content = f.read()

            doc_id = filepath.stem  # Use filename without extension as ID

            logger.info(f"Loaded Markdown file: {filepath.name}")

            return Document(content=content, metadata=metadata, doc_id=doc_id)
        except Exception as e:
            logger.error(f"Error loading Markdown file {filepath}: {e}")
            raise

    def _get_organized_path(
        self, asignatura: str, tipo_documento: str, filename: str
    ) -> Path:
        """
        Get the organized file path following the directory structure.

        Normalizes subject and document type names and creates the directory
        structure: asignatura/tipo-documento/filename

        Args:
            asignatura: Subject name
            tipo_documento: Document type
            filename: File name

        Returns:
            Path to the file in the organized structure
        """
        asignatura_norm = asignatura.lower().replace(" ", "-").replace("_", "-")
        tipo_documento_norm = tipo_documento.lower().replace(" ", "-").replace("_", "-")

        subject_dir = self.documents_path / asignatura_norm / tipo_documento_norm
        subject_dir.mkdir(parents=True, exist_ok=True)

        return subject_dir / filename

    def load_file(self, filename: str, metadata: DocumentMetadata) -> Document:
        """
        Load a file based on its extension and metadata.

        Automatically detects file type and uses appropriate loader.
        Searches in organized path (asignatura/tipo_documento) first, then root.

        Args:
            filename: Name or path of the file to load
            metadata: Document metadata including subject and type

        Returns:
            Document object with content and metadata

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file type is unsupported

        Example:
            metadata = DocumentMetadata(
                filename="tema1.pdf",
                asignatura="iv",
                tipo_documento="teoria"
            )
            doc = loader.load_file("tema1.pdf", metadata)
        """
        if metadata.asignatura and metadata.tipo_documento:
            filepath = self._get_organized_path(
                metadata.asignatura, metadata.tipo_documento, filename
            )

            if not filepath.exists():
                filepath = self.documents_path / filename
        else:
            filepath = self.documents_path / filename

        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        extension = filepath.suffix.lower()

        if extension == ".txt":
            return self.load_text_file(filepath, metadata)
        elif extension == ".pdf":
            return self.load_pdf_file(filepath, metadata)
        elif extension in [".md", ".markdown"]:
            return self.load_markdown_file(filepath, metadata)
        else:
            raise ValueError(f"Unsupported file type: {extension}")

    def save_uploaded_file(
        self, file_content: bytes, filename: str, asignatura: str, tipo_documento: str
    ) -> Path:
        """
        Save an uploaded file to the organized directory structure.

        Creates necessary directories and saves the file content in the
        appropriate location: documents/asignatura/tipo-documento/filename

        Args:
            file_content: Binary content of the file
            filename: Name for the saved file
            asignatura: Subject name for organization
            tipo_documento: Document type for organization

        Returns:
            Path where the file was saved

        Raises:
            Exception: If file saving fails

        Example:
            saved_path = loader.save_uploaded_file(
                file_content=pdf_bytes,
                filename="nuevo-tema.pdf",
                asignatura="iv",
                tipo_documento="teoria"
            )
        """
        try:
            filepath = self._get_organized_path(asignatura, tipo_documento, filename)
            with open(filepath, "wb") as f:
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
    Get the global file loader instance (singleton pattern).

    Creates a new FileLoader on first call and reuses it for subsequent calls.

    Returns:
        FileLoader instance
    """
    global _file_loader
    if _file_loader is None:
        _file_loader = FileLoader()
    return _file_loader
