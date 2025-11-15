"""
Vector store operations using Qdrant for semantic search.

This module provides the VectorStoreService class that manages document indexing
and retrieval using Qdrant as the vector database. It handles:

- Collection initialization and management
- Document chunking and embedding generation
- Semantic search with metadata filtering
- Point creation and storage in Qdrant

Architecture:
    Documents -> Chunking -> Embedding -> Qdrant Points -> Search

The service uses:
- Qdrant Client for vector database operations
- Embedding service for text vectorization
- Document processor for text chunking
- COSINE distance for similarity computation

Example:
    vector_store = get_vector_store()

    # Index documents
    indexed = vector_store.index_documents(documents)

    # Search with filters
    results = vector_store.search(
        query="What is Docker?",
        top_k=5,
        filters={"asignatura": "iv"}
    )
"""

import logging
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from rag_service.config import settings
from rag_service.documents.document_processor import get_document_processor
from rag_service.embeddings import get_embedding_service
from rag_service.models import Document, SearchResult

logger = logging.getLogger(__name__)


class VectorStoreService:
    """
    Service for managing Qdrant vector store.

    This service handles document indexing and semantic search using Qdrant
    as the vector database and embedding service for text vectorization.
    """

    def __init__(self):
        logger.info(
            f"Connecting to Qdrant at {settings.qdrant_host}:{settings.qdrant_port}"
        )

        self.client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
        )

        self.collection_name = settings.qdrant_collection_name
        self.embedding_service = get_embedding_service()

        # Initialize collection if it doesn't exist
        self._init_collection()

    def _init_collection(self):
        """
        Initialize Qdrant collection if it doesn't exist.

        Creates a new collection with COSINE distance metric and the configured
        embedding dimension. If the collection already exists, no action is taken.

        Raises:
            Exception: If collection creation fails
        """
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

    def _create_points(
        self, documents: list[Document], embeddings: list[list[float]]
    ) -> list[PointStruct]:
        """
        Create Qdrant points from documents and their embeddings.

        Args:
            documents: List of documents to convert to points
            embeddings: List of embedding vectors corresponding to documents

        Returns:
            List of PointStruct objects ready to be uploaded to Qdrant
        """
        points = []
        for idx, (doc, embedding) in enumerate(zip(documents, embeddings, strict=True)):
            point = PointStruct(
                id=idx,
                vector=embedding,
                payload={
                    "content": doc.content,
                    **doc.metadata.model_dump(),
                },
            )
            points.append(point)
        return points

    def index_documents(
        self, documents: list[Document], auto_chunk: bool = True
    ) -> int:
        """
        Index documents into the vector store.

        This method processes documents through chunking (if enabled), generates
        embeddings, and stores them in Qdrant for semantic search.

        Args:
            documents: List of documents to index
            auto_chunk: Whether to automatically chunk documents (default: True)

        Returns:
            Number of document chunks successfully indexed

        Raises:
            Exception: If indexing fails
        """
        if not documents:
            logger.warning("No documents to index")
            return 0

        try:
            # Chunk documents if requested
            if auto_chunk:
                logger.info(f"Chunking {len(documents)} documents...")
                processor = get_document_processor()
                documents = processor.chunk_documents(documents)
                logger.info(f"After chunking: {len(documents)} chunks to index")

            # Generate embeddings for all document chunks
            texts = [doc.content for doc in documents]
            logger.info(f"Generating embeddings for {len(texts)} chunks")
            embeddings = self.embedding_service.embed_documents(texts)

            # Create Qdrant points from documents and embeddings
            points = self._create_points(documents, embeddings)

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
        score_threshold: float = 0.5,
        filters: dict[str, str] | None = None,
    ) -> list[SearchResult]:
        """
        Perform semantic search over indexed documents.

        Converts the query to an embedding vector and searches for similar documents
        in the Qdrant collection. Supports metadata filtering and score thresholds.

        Args:
            query: Natural language search query
            top_k: Maximum number of results to return (default: 5)
            score_threshold: Minimum similarity score (0-1) for results (default: 0.5)
            filters: Optional metadata filters (e.g., {"asignatura": "iv"})

        Returns:
            List of SearchResult objects sorted by relevance score

        Raises:
            Exception: If search fails

        Example:
            results = vector_store.search(
                query="What is continuous integration?",
                top_k=3,
                score_threshold=0.7,
                filters={"asignatura": "iv", "tipo_documento": "teoria"}
            )
        """
        try:
            logger.info(f"Searching for: '{query}'")
            query_embedding = self.embedding_service.embed_query(query)

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

            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k,
                score_threshold=score_threshold,
                query_filter=qdrant_filter,
            )

            results = []
            for result in search_results:
                search_result = SearchResult(
                    content=result.payload.get("content", ""),
                    metadata=result.payload,
                    score=result.score,
                )
                results.append(search_result)

            logger.info(
                f"Found {len(results)} results above threshold {score_threshold}"
            )
            return results

        except Exception as e:
            logger.error(f"Error during search: {e}")
            raise

    def delete_collection(self):
        """
        Delete the Qdrant collection and all its data.

        WARNING: This operation is irreversible and will delete all indexed documents.

        Raises:
            Exception: If deletion fails
        """
        try:
            self.client.delete_collection(collection_name=self.collection_name)
            logger.info(f"Deleted collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")
            raise

    def get_collection_info(self) -> dict[str, Any]:
        """
        Get information about the Qdrant collection.

        Returns:
            Dictionary with collection metadata:
                - name: Collection name
                - vectors_count: Number of vectors stored
                - points_count: Number of points stored
                - status: Collection status

        Raises:
            Exception: If retrieval fails
        """
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
    Get the global vector store instance (singleton pattern).

    Creates a new VectorStoreService instance on first call and reuses it
    for subsequent calls to ensure single connection to Qdrant.

    Returns:
        VectorStoreService instance
    """
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStoreService()
    return _vector_store
