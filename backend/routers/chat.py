import httpx
from fastapi import APIRouter, Depends, HTTPException, Request

from backend.config import settings
from backend.dependencies import get_current_user
from backend.models import UserInDB, UserRole

router = APIRouter(tags=["chat"])


@router.post("/chat")
async def chat(request: Request, user: UserInDB = Depends(get_current_user)):
    # Forward to chatbot service
    # Increase timeout for chatbot response (LLM generation can be slow)
    async with httpx.AsyncClient(timeout=120.0) as client:
        json_data = await request.json()

        # Validate subject access
        requested_subject = json_data.get("asignatura")
        if requested_subject:
            # If user is student, check if they are enrolled
            if user.role == UserRole.STUDENT and requested_subject not in user.subjects:
                raise HTTPException(
                    status_code=403, detail="Not enrolled in this subject"
                )

        response = await client.post(
            f"{settings.CHATBOT_SERVICE_URL}/chat", json=json_data
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code, detail=response.json()
            )
        return response.json()
