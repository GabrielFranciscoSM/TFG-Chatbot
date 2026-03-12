import httpx
from fastapi import APIRouter, Depends, HTTPException, Request

from backend.config import settings
from backend.dependencies import require_admin_or_professor
from backend.models import UserInDB

router = APIRouter(
    prefix="/professor/subjects/{subject_id}/faqs", tags=["faqs-professor"]
)
public_router = APIRouter(prefix="/subjects/{subject_id}/faqs", tags=["faqs-public"])


@router.post("/generate")
async def generate_faqs(
    subject_id: str,
    request: Request,
    user: UserInDB = Depends(require_admin_or_professor),
):
    """Generate FAQs for a subject. Proxies to math_service."""
    if subject_id not in user.subjects:
        raise HTTPException(status_code=403, detail="You don't teach this subject")

    json_data = await request.json()
    # Add subject to payload
    json_data["subject"] = subject_id

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{settings.math_service_url}/faqs/generate", json=json_data
            )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503, detail=f"Math service unavailable: {e}"
        ) from e

    if response.status_code != 200:
        try:
            detail = response.json()
        except Exception:
            detail = {"error": response.text or "Unknown error in math service"}
        raise HTTPException(status_code=response.status_code, detail=detail)
    return response.json()


@router.post("")
async def create_faq(
    subject_id: str,
    request: Request,
    user: UserInDB = Depends(require_admin_or_professor),
):
    """Create a manual FAQ for a subject. Proxies to math_service."""
    if subject_id not in user.subjects:
        raise HTTPException(status_code=403, detail="You don't teach this subject")

    json_data = await request.json()

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.math_service_url}/faqs/{subject_id}", json=json_data
            )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503, detail=f"Math service unavailable: {e}"
        ) from e

    if response.status_code != 200:
        try:
            detail = response.json()
        except Exception:
            detail = {"error": response.text or "Unknown error in math service"}
        raise HTTPException(status_code=response.status_code, detail=detail)
    return response.json()


@router.get("")
async def get_professor_faqs(
    subject_id: str, user: UserInDB = Depends(require_admin_or_professor)
):
    """Get all FAQs for a subject (including drafts). Proxies to math_service."""
    if subject_id not in user.subjects:
        raise HTTPException(status_code=403, detail="You don't teach this subject")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{settings.math_service_url}/faqs/{subject_id}"
            )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503, detail=f"Math service unavailable: {e}"
        ) from e

    if response.status_code != 200:
        try:
            detail = response.json()
        except Exception:
            detail = {"error": response.text or "Unknown error in math service"}
        raise HTTPException(status_code=response.status_code, detail=detail)
    return response.json()


@router.put("/{faq_id}")
async def update_faq(
    subject_id: str,
    faq_id: str,
    request: Request,
    user: UserInDB = Depends(require_admin_or_professor),
):
    """Update an FAQ. Proxies to math_service."""
    if subject_id not in user.subjects:
        raise HTTPException(status_code=403, detail="You don't teach this subject")

    json_data = await request.json()

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.put(
                f"{settings.math_service_url}/faqs/{subject_id}/{faq_id}",
                json=json_data,
            )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503, detail=f"Math service unavailable: {e}"
        ) from e

    if response.status_code != 200:
        try:
            detail = response.json()
        except Exception:
            detail = {"error": response.text or "Unknown error in math service"}
        raise HTTPException(status_code=response.status_code, detail=detail)
    return response.json()


@router.delete("/{faq_id}")
async def delete_faq(
    subject_id: str, faq_id: str, user: UserInDB = Depends(require_admin_or_professor)
):
    """Delete an FAQ. Proxies to math_service."""
    if subject_id not in user.subjects:
        raise HTTPException(status_code=403, detail="You don't teach this subject")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.delete(
                f"{settings.math_service_url}/faqs/{subject_id}/{faq_id}"
            )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503, detail=f"Math service unavailable: {e}"
        ) from e

    if response.status_code != 200:
        try:
            detail = response.json()
        except Exception:
            detail = {"error": response.text or "Unknown error in math service"}
        raise HTTPException(status_code=response.status_code, detail=detail)
    return response.json()


@router.patch("/{faq_id}/publish")
async def publish_faq(
    subject_id: str, faq_id: str, user: UserInDB = Depends(require_admin_or_professor)
):
    """Publish an FAQ. Proxies to math_service."""
    if subject_id not in user.subjects:
        raise HTTPException(status_code=403, detail="You don't teach this subject")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.patch(
                f"{settings.math_service_url}/faqs/{subject_id}/{faq_id}/publish"
            )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503, detail=f"Math service unavailable: {e}"
        ) from e

    if response.status_code != 200:
        try:
            detail = response.json()
        except Exception:
            detail = {"error": response.text or "Unknown error in math service"}
        raise HTTPException(status_code=response.status_code, detail=detail)
    return response.json()


@router.patch("/{faq_id}/unpublish")
async def unpublish_faq(
    subject_id: str, faq_id: str, user: UserInDB = Depends(require_admin_or_professor)
):
    """Unpublish an FAQ. Proxies to math_service."""
    if subject_id not in user.subjects:
        raise HTTPException(status_code=403, detail="You don't teach this subject")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.patch(
                f"{settings.math_service_url}/faqs/{subject_id}/{faq_id}/unpublish"
            )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503, detail=f"Math service unavailable: {e}"
        ) from e

    if response.status_code != 200:
        try:
            detail = response.json()
        except Exception:
            detail = {"error": response.text or "Unknown error in math service"}
        raise HTTPException(status_code=response.status_code, detail=detail)
    return response.json()


@public_router.get("")
async def get_public_faqs(subject_id: str):
    """Get published FAQs for a subject. Proxies to math_service and filters."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{settings.math_service_url}/faqs/{subject_id}"
            )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503, detail=f"Math service unavailable: {e}"
        ) from e

    if response.status_code != 200:
        try:
            detail = response.json()
        except Exception:
            detail = {"error": response.text or "Unknown error in math service"}
        raise HTTPException(status_code=response.status_code, detail=detail)

    # Filter for only published FAQs
    all_faqs = response.json()
    published_faqs = [faq for faq in all_faqs if faq.get("status") == "published"]
    return published_faqs
