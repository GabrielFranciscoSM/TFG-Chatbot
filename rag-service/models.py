"""Data models for RAG service."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class DocumentMetadata(BaseModel):
    """Metadata schema for indexed documents."""
    
    asignatura: str = Field(..., description="Subject name, e.g., 'Lógica Difusa'")
    tipo_documento: str = Field(..., description="Document type: 'apuntes', 'ejercicios', 'examen', etc.")
    fecha: str = Field(..., description="Date in ISO format: YYYY-MM-DD")
    tema: Optional[str] = Field(None, description="Topic within the subject")
    autor: Optional[str] = Field(None, description="Document author")
    fuente: str = Field(default="PRADO UGR", description="Source: 'PRADO UGR', 'Wikipedia', etc.")
    idioma: str = Field(default="es", description="Language code: 'es' or 'en'")
    chunk_id: Optional[int] = Field(None, description="Chunk ID within the document")
    
    class Config:
        json_schema_extra = {
            "example": {
                "asignatura": "Lógica Difusa",
                "tipo_documento": "apuntes",
                "fecha": "2025-10-14",
                "tema": "Conjuntos difusos",
                "fuente": "PRADO UGR",
                "idioma": "es",
                "chunk_id": 0
            }
        }


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
