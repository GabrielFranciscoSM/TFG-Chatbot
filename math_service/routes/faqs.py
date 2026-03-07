from bson import ObjectId
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from math_service.models import FAQGenerateRequest, FAQGenerateResponse
from math_service.services.faq_service import FAQService

router = APIRouter(prefix="/faqs", tags=["faqs"])


class FAQUpdateRequest(BaseModel):
    question: str | None = None
    answer: str | None = None
    status: str | None = None


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
        cursor = service.faq_collection.find({"subject": subject_id})
        # Sort by cluster size descending to show most common first
        faqs = []
        for doc in cursor.sort("cluster_size", -1):
            doc["id"] = str(doc.pop("_id", ""))
            faqs.append(doc)
        return faqs
    finally:
        service.close()


@router.put("/{subject_id}/{faq_id}")
def update_faq(subject_id: str, faq_id: str, request: FAQUpdateRequest) -> dict:
    """Update an existing FAQ."""
    service = FAQService()
    try:
        if not ObjectId.is_valid(faq_id):
            raise HTTPException(status_code=400, detail="Invalid FAQ ID")

        update_data = {k: v for k, v in request.model_dump().items() if v is not None}
        if not update_data:
            return {"status": "success", "message": "No changes provided"}

        result = service.faq_collection.update_one(
            {"_id": ObjectId(faq_id), "subject": subject_id}, {"$set": update_data}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="FAQ not found")
        return {"status": "success", "message": "FAQ updated"}
    finally:
        service.close()


@router.patch("/{subject_id}/{faq_id}/publish")
def publish_faq(subject_id: str, faq_id: str) -> dict:
    """Publish an FAQ."""
    service = FAQService()
    try:
        if not ObjectId.is_valid(faq_id):
            raise HTTPException(status_code=400, detail="Invalid FAQ ID")

        result = service.faq_collection.update_one(
            {"_id": ObjectId(faq_id), "subject": subject_id},
            {"$set": {"status": "published"}},
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="FAQ not found")
        return {"status": "success", "message": "FAQ published"}
    finally:
        service.close()


@router.patch("/{subject_id}/{faq_id}/unpublish")
def unpublish_faq(subject_id: str, faq_id: str) -> dict:
    """Unpublish an FAQ by setting its status back to draft."""
    service = FAQService()
    try:
        if not ObjectId.is_valid(faq_id):
            raise HTTPException(status_code=400, detail="Invalid FAQ ID")

        result = service.faq_collection.update_one(
            {"_id": ObjectId(faq_id), "subject": subject_id},
            {"$set": {"status": "draft"}},
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="FAQ not found")
        return {"status": "success", "message": "FAQ unpublished"}
    finally:
        service.close()


@router.delete("/{subject_id}/{faq_id}")
def delete_faq(subject_id: str, faq_id: str) -> dict:
    """Delete an FAQ."""
    service = FAQService()
    try:
        if not ObjectId.is_valid(faq_id):
            raise HTTPException(status_code=400, detail="Invalid FAQ ID")

        result = service.faq_collection.delete_one(
            {"_id": ObjectId(faq_id), "subject": subject_id}
        )
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="FAQ not found")
        return {"status": "success", "message": "FAQ deleted"}
    finally:
        service.close()
