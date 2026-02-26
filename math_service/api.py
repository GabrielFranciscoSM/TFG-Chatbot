"""
FastAPI application for the Math service.

This service provides REST API endpoints for mathematical analysis
of educational content, including FAQ generation and topic extraction
using NLP and clustering techniques from `math_investigation`.

Architecture:
    - FAQ Generation: Cluster student questions and generate FAQs
    - Topic Extraction: Extract main topics from academic documents
    - Analysis API: On-demand analysis of uploaded content

Main Routes:
    - /health: Health check endpoint

The service runs independently and can be accessed by the main backend
through HTTP requests for analysis operations.

Example:
    Start the service:
        uvicorn math_service.api:app --reload --port 8083

    Or use the Docker container:
        docker compose up math_service
"""

__version__ = "0.1.0"


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from math_service.config import settings
from math_service.logging_config import CorrelationIdMiddleware, setup_logging
from math_service.routes.general import router as general_router

# Create FastAPI app
app = FastAPI(
    title="Math Service",
    description="Mathematical analysis service for educational chatbot",
    version=__version__,
)

# Initialize Prometheus instrumentator
Instrumentator().instrument(app).expose(app)

# Initialize structured logging
setup_logging()

# Add correlation ID middleware
app.add_middleware(CorrelationIdMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(general_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "math_service.api:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
    )
