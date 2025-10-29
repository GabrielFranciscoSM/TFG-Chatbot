"""Data models for RAG service."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class HealthCheckResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str = Field(..., description="Health status of the API, e.g., 'healthy' or 'unhealthy'")
    qdrant_connected: bool = Field(..., description="Whether Qdrant vector store is connected")
    collection: dict | None = Field(None, description="Collection information from vector store")
    message: str | None = Field(None, description="Additional message about the health status")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "healthy",
                "qdrant_connected": True,
                "collection": {
                    "name": "academic_documents",
                    "vectors_count": 0,
                    "points_count": 52,
                    "status": "green"
                },
                "message": "API is healthy and running"
            }
        }
    )

class DocumentMetadata(BaseModel):
    """Metadata schema for indexed documents."""
    
    filename: Optional[str] = Field(None, description="Original file name of the document")
    asignatura: str = Field(..., description="Subject name, e.g., 'Lógica Difusa'")
    tipo_documento: str = Field(..., description="Document type: 'apuntes', 'ejercicios', 'examen', etc.")
    fecha: str = Field(..., description="Date in ISO format: YYYY-MM-DD")
    tema: Optional[str] = Field(None, description="Topic within the subject")
    autor: Optional[str] = Field(None, description="Document author")
    fuente: str = Field(default="PRADO UGR", description="Source: 'PRADO UGR', 'Wikipedia', etc.")
    idioma: str = Field(default="es", description="Language code: 'es' or 'en'")
    chunk_id: Optional[int] = Field(None, description="Chunk ID within the document")
    licencia: Optional[str] = Field(None, description="Document license, e.g., 'CC-BY', 'MIT', etc.")


    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "asignatura": "Lógica Difusa",
                "tipo_documento": "apuntes",
                "fecha": "2025-10-14",
                "tema": "Conjuntos difusos",
                "fuente": "PRADO UGR",
                "idioma": "es",
                "licencia": "CC-BY",
                "chunk_id": 0
            }
        }
    )


class Document(BaseModel):
    """Document to be indexed."""
    
    content: str = Field(..., description="Document content/text")
    metadata: DocumentMetadata = Field(..., description="Document metadata")
    doc_id: Optional[str] = Field(None, description="Optional document ID")


class QueryRequest(BaseModel):
    """Request for semantic search."""
    
    query: str = Field(..., description="Search query")
    asignatura: Optional[str] = Field(None, description="Filter by subject")
    tipo_documento: Optional[str] = Field(None, description="Filter by document type")
    top_k: Optional[int] = Field(5, description="Number of results to return")
    similarity_threshold: Optional[float] = Field(0.7, description="Minimum similarity score")
    

class SearchResult(BaseModel):
    """Single search result."""
    
    content: str = Field(..., description="Document content")
    metadata: Dict[str, Any] = Field(..., description="Document metadata")
    score: float = Field(..., description="Similarity score")


class QueryResponse(BaseModel):
    """Response for semantic search."""
    
    results: List[SearchResult] = Field(..., description="Search results")
    total_results: int = Field(..., description="Total number of results")
    query: str = Field(..., description="Original query")


class IndexResponse(BaseModel):
    """Response after indexing documents."""
    
    indexed_count: int = Field(..., description="Number of documents indexed")
    collection_name: str = Field(..., description="Qdrant collection name")
    timestamp: datetime = Field(default_factory=datetime.now, description="Indexing timestamp")


class LoadFileRequest(BaseModel):
    """Request to load a file from the documents directory."""
    
    filename: str = Field(..., description="Name of the file to load")
    metadata: DocumentMetadata = Field(..., description="Metadata for the document")


class LoadFileResponse(BaseModel):
    """Response after loading a file."""
    
    filename: str = Field(..., description="Name of the loaded file")
    doc_id: str = Field(..., description="Document ID")
    indexed_count: int = Field(..., description="Number of chunks indexed")
    timestamp: datetime = Field(default_factory=datetime.now, description="Load timestamp")


class FileListResponse(BaseModel):
    """Response with list of files."""
    
    files: List[str] = Field(..., description="List of available files")
    total_files: int = Field(..., description="Total number of files")


class SubjectListResponse(BaseModel):
    """Response with list of subjects."""
    
    subjects: List[str] = Field(..., description="List of available subjects")
    total_subjects: int = Field(..., description="Total number of subjects")


class DocumentTypesResponse(BaseModel):
    """Response with list of document types for a subject."""
    
    asignatura: str = Field(..., description="Subject name")
    document_types: List[str] = Field(..., description="List of document types")
    total_types: int = Field(..., description="Total number of document types")


class UploadFileMetadata(DocumentMetadata):
    """Metadata for file upload, inherits from DocumentMetadata."""
    auto_index: bool = Field(default=True, description="Automatically index after upload")

class MessageResponse(BaseModel):
    message: str = Field(..., description="Response message from the API")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"message": "Hello World"}
        }
    )
