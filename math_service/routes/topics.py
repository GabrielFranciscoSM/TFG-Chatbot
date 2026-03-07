"""
Topic Extraction Routes.

Endpoints to extract topics and concept maps from documents using NLP
and retrieve extracted results.
"""

from fastapi import APIRouter, HTTPException

from math_service.models import TopicExtractRequest, TopicResult
from math_service.services.topic_service import TopicService

router = APIRouter(prefix="/topics", tags=["topics"])


@router.post("/extract", response_model=TopicResult)
def extract_topics(request: TopicExtractRequest) -> TopicResult:
    """
    Extract topics for a given subject using TF-IDF/BoW and NMF.

    Returns the main topics and a concept map of terms.
    """
    service = TopicService()
    try:
        result = service.extract_topics(
            subject=request.subject, vectorizer_type=request.vectorizer_type
        )

        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=result.get("message"))

        return TopicResult(**result)
    finally:
        service.close()


@router.get("/{subject_id}")
def get_topics_by_subject(subject_id: str) -> list[dict]:
    """Retrieve existing topic extractions for a subject."""
    service = TopicService()
    try:
        # Fetch topic results for the given subject from MongoDB
        # Return them sorted by creation time descending (latest first)
        cursor = service.collection.find({"subject": subject_id}, {"_id": 0}).sort(
            "created_at", -1
        )
        return list(cursor)
    finally:
        service.close()
