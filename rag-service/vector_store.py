"""Vector store operations using Qdrant."""

from typing import List, Dict, Any, Optional
import logging
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from langchain_qdrant import QdrantVectorStore

from rag_service.config import settings
from rag_service.embeddings import get_embedding_service
from rag_service.models import Document, SearchResult
from rag_service.document_processor import get_document_processor

logger = logging.getLogger(__name__)


class VectorStoreService:
    """Service for managing Qdrant vector store."""
    
    def __init__(self):
        """Initialize Qdrant client and collection."""
        logger.info(f"Connecting to Qdrant at {settings.qdrant_host}:{settings.qdrant_port}")
        
        self.client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
        )
        
        self.collection_name = settings.qdrant_collection_name
        self.embedding_service = get_embedding_service()
        
        # Initialize collection if it doesn't exist
        self._init_collection()
    
    def _init_collection(self):
        """Create collection if it doesn't exist."""
        try:
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if self.collection_name not in collection_names:
                logger.info(f"Creating collection: {self.collection_name}")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=settings.embedding_dimension,
                        distance=Distance.COSINE,
                    ),
                )
                logger.info(f"Collection '{self.collection_name}' created successfully")
            else:
                logger.info(f"Collection '{self.collection_name}' already exists")
        except Exception as e:
            logger.error(f"Error initializing collection: {e}")
            raise
    
    def index_documents(self, documents: List[Document], auto_chunk: bool = True) -> int:
        """
        Index documents into Qdrant.
        
        Args:
            documents: List of documents to index
            auto_chunk: Whether to automatically chunk documents (default: True)
            
        Returns:
            Number of chunks/documents indexed
        """
        if not documents:
            logger.warning("No documents to index")
            return 0
        
        try:
            # Chunk documents if auto_chunk is enabled
            if auto_chunk:
                logger.info(f"Chunking {len(documents)} documents...")
                processor = get_document_processor()
                documents = processor.chunk_documents(documents)
                logger.info(f"After chunking: {len(documents)} chunks to index")
            
            # Extract texts for embedding
            texts = [doc.content for doc in documents]
            
            # Generate embeddings
            logger.info(f"Generating embeddings for {len(texts)} chunks")
            embeddings = self.embedding_service.embed_documents(texts)
            
            # Prepare points for Qdrant
            points = []
            for idx, (doc, embedding) in enumerate(zip(documents, embeddings)):
                point = PointStruct(
                    id=idx,  # Can be improved with UUID or hash
                    vector=embedding,
                    payload={
                        "content": doc.content,
                        **doc.metadata.model_dump(),
                    }
                )
                points.append(point)
            
            # Upload to Qdrant
            logger.info(f"Uploading {len(points)} points to Qdrant")
            self.client.upsert(
                collection_name=self.collection_name,
                points=points,
            )
            
            logger.info(f"Successfully indexed {len(points)} documents")
            return len(points)
            
        except Exception as e:
            logger.error(f"Error indexing documents: {e}")
            raise
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.7,
        filters: Optional[Dict[str, str]] = None,
    ) -> List[SearchResult]:
        """
        Semantic search in Qdrant with optional metadata filtering.
        
        Args:
            query: Search query
            top_k: Number of results to return
            score_threshold: Minimum similarity score
            filters: Optional metadata filters (e.g., {"asignatura": "Lógica Difusa"})
            
        Returns:
            List of search results
        """
        try:
            # Generate query embedding
            logger.info(f"Searching for: '{query}'")
            query_embedding = self.embedding_service.embed_query(query)
            
            # Build Qdrant filter
            qdrant_filter = None
            if filters:
                conditions = []
                for key, value in filters.items():
                    conditions.append(
                        FieldCondition(
                            key=key,
                            match=MatchValue(value=value),
                        )
                    )
                if conditions:
                    qdrant_filter = Filter(must=conditions)
                    logger.debug(f"Applying filters: {filters}")
            
            # Search in Qdrant
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k,
                score_threshold=score_threshold,
                query_filter=qdrant_filter,
            )
            
            # Convert to SearchResult objects
            results = []
            for result in search_results:
                search_result = SearchResult(
                    content=result.payload.get("content", ""),
                    metadata=result.payload,
                    score=result.score,
                )
                results.append(search_result)
            
            logger.info(f"Found {len(results)} results above threshold {score_threshold}")
            return results
            
        except Exception as e:
            logger.error(f"Error during search: {e}")
            raise
    
    def delete_collection(self):
        """Delete the collection (useful for testing)."""
        try:
            self.client.delete_collection(collection_name=self.collection_name)
            logger.info(f"Deleted collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")
            raise
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection."""
        try:
            info = self.client.get_collection(collection_name=self.collection_name)
            return {
                "name": self.collection_name,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "status": info.status,
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            raise


# Global vector store instance
_vector_store: VectorStoreService | None = None


def get_vector_store() -> VectorStoreService:
    """
    Get or create the global vector store instance.
    
    Returns:
        VectorStoreService instance
    """
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStoreService()
    return _vector_store
