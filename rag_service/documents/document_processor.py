"""Document processing and chunking utilities."""

from typing import List, Optional
import logging
from langchain.text_splitter import RecursiveCharacterTextSplitter

from rag_service.models import Document

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Service for processing and chunking documents."""
    
    def __init__(
        self,
        chunk_size: int = 250,
        chunk_overlap: int = 50,
        separators: Optional[List[str]] = None,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        if separators is None:
            separators = [
                "\n\n",
                "\n",
                ". ",
                ", ",
                " ",
                "",
            ]
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=separators,
            length_function=len,
        )
        
        logger.info(
            f"Initialized DocumentProcessor: "
            f"chunk_size={chunk_size}, chunk_overlap={chunk_overlap}"
        )
    
    def chunk_document(self, document: Document) -> List[Document]:
        if len(document.content) <= self.chunk_size:
            logger.debug(f"Document is short ({len(document.content)} chars), no chunking needed")
            if document.metadata.chunk_id is None:
                document.metadata.chunk_id = 0
            return [document]
        
        chunks = self.text_splitter.split_text(document.content)
        logger.info(f"Split document into {len(chunks)} chunks")
        
        chunked_docs = []
        for idx, chunk_text in enumerate(chunks):
            chunk_metadata = document.metadata.model_copy(deep=True)
            chunk_metadata.chunk_id = idx
            chunk_metadata.filename = document.metadata.filename
            
            chunked_doc = Document(
                content=chunk_text,
                metadata=chunk_metadata,
                doc_id=f"{document.doc_id}_chunk_{idx}" if document.doc_id else None,
            )
            chunked_docs.append(chunked_doc)
        
        logger.debug(f"Created {len(chunked_docs)} chunked documents")
        return chunked_docs
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        all_chunks = []
        for doc in documents:
            chunks = self.chunk_document(doc)
            all_chunks.extend(chunks)
        
        logger.info(
            f"Chunked {len(documents)} documents into {len(all_chunks)} total chunks"
        )
        return all_chunks
    
    def estimate_tokens(self, text: str) -> int:
        return len(text) // 4


# Global document processor instance
_document_processor: DocumentProcessor | None = None

def get_document_processor(
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> DocumentProcessor:
    global _document_processor
    if _document_processor is None:
        _document_processor = DocumentProcessor(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
    return _document_processor
