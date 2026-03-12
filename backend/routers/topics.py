import httpx
from fastapi import APIRouter, Depends, HTTPException, Request

from backend.config import settings
from backend.dependencies import require_admin_or_professor
from backend.models import UserInDB

router = APIRouter(
    prefix="/professor/subjects/{subject_id}/topics", tags=["topics-professor"]
)


@router.post("/extract")
async def extract_topics(
    subject_id: str,
    request: Request,
    user: UserInDB = Depends(require_admin_or_professor),
):
    """Extract topics for a subject. Proxies to math_service."""
    if subject_id not in user.subjects:
        raise HTTPException(status_code=403, detail="You don't teach this subject")

    json_data = await request.json()
    # Add subject to payload
    json_data["subject"] = subject_id

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{settings.math_service_url}/topics/extract", json=json_data
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
async def get_topics(
    subject_id: str, user: UserInDB = Depends(require_admin_or_professor)
):
    """Get all topics extractions for a subject. Proxies to math_service."""
    if subject_id not in user.subjects:
        raise HTTPException(status_code=403, detail="You don't teach this subject")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{settings.math_service_url}/topics/{subject_id}"
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
