"""FastAPI application for RAG service."""

__version__ = "0.1.0"

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings

from .routes.general import router as general_router
from .routes.search_index import router as search_index_router
from .routes.files import router as files_router
from .routes.subjects import router as subjects_router

# Create FastAPI app
app = FastAPI(
    title="RAG Service",
    description="Retrieval-Augmented Generation service for educational chatbot",
    version=__version__,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(general_router)
app.include_router(search_index_router)
app.include_router(files_router)
app.include_router(subjects_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "rag_service.api:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
    )
