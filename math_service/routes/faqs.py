"""
FAQ Generation Routes.

Endpoints to generate FAQs for subjects based on student questions
and retrieve generated FAQs.
"""

from fastapi import APIRouter, HTTPException

from math_service.models import FAQGenerateRequest, FAQGenerateResponse
from math_service.services.faq_service import FAQService

router = APIRouter(prefix="/faqs", tags=["faqs"])


@router.post("/generate", response_model=FAQGenerateResponse)
def generate_faqs(request: FAQGenerateRequest) -> FAQGenerateResponse:
    """
    Generate FAQs for a given subject using clustering and NLP.

    Extracts questions from past student interactions and groups them
    to find representative questions.
    """
    service = FAQService()
    try:
        result = service.generate_faqs(
            subject=request.subject, min_cluster_size=request.min_cluster_size
        )

        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=result.get("message"))

        return FAQGenerateResponse(**result)

    finally:
        service.close()


@router.get("/{subject_id}")
def get_faqs_by_subject(subject_id: str) -> list[dict]:
    """Retrieve existing generated FAQs for a subject."""
    service = FAQService()
    try:
        # Fetch FAQs for the given subject from MongoDB
        cursor = service.faq_collection.find({"subject": subject_id}, {"_id": 0})
        # Sort by cluster size descending to show most common first
        faqs = list(cursor.sort("cluster_size", -1))
        return faqs
    finally:
        service.close()
