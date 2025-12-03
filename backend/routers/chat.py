from datetime import UTC, datetime

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request

from backend.config import settings
from backend.dependencies import get_current_user, get_sessions_collection
from backend.models import UserInDB, UserRole

router = APIRouter(tags=["chat"])


@router.post("/chat")
async def chat(
    request: Request,
    user: UserInDB = Depends(get_current_user),
    collection=Depends(get_sessions_collection),
):
    # Forward to chatbot service
    # Increase timeout for chatbot response (LLM generation can be slow)
    async with httpx.AsyncClient(timeout=120.0) as client:
        json_data = await request.json()
        session_id = json_data.get("id")

        if not session_id:
            raise HTTPException(status_code=422, detail="Session ID is required")

        # Validate session ownership and persistence
        session = collection.find_one({"_id": session_id})

        if session:
            if session["user_id"] != user.username:
                raise HTTPException(
                    status_code=403, detail="Not authorized to access this session"
                )

            # Update last_active
            collection.update_one(
                {"_id": session_id}, {"$set": {"last_active": datetime.now(UTC)}}
            )
        else:
            # Auto-create session if it doesn't exist (for backward compatibility and ease of use)
            requested_subject = json_data.get("asignatura")

            # Validate subject access if provided (allow "general" for everyone)
            if requested_subject and requested_subject != "general":
                if (
                    user.role == UserRole.STUDENT
                    and requested_subject not in user.subjects
                ):
                    raise HTTPException(
                        status_code=403, detail="Not enrolled in this subject"
                    )

            now = datetime.now(UTC)
            new_session = {
                "_id": session_id,
                "user_id": user.username,
                "title": "New Chat",
                "subject": requested_subject or "general",
                "created_at": now,
                "last_active": now,
            }
            collection.insert_one(new_session)

        # Validate subject access (redundant if new session, but safe for existing ones)
        requested_subject = json_data.get("asignatura")
        if requested_subject and requested_subject != "general":
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


@router.get("/history/{session_id}")
async def get_history(
    session_id: str,
    user: UserInDB = Depends(get_current_user),
    collection=Depends(get_sessions_collection),
):
    """Get conversation history for a session."""
    # Validate session ownership
    session = collection.find_one({"_id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session["user_id"] != user.username:
        raise HTTPException(
            status_code=403, detail="Not authorized to access this session"
        )

    # Forward to chatbot service
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{settings.CHATBOT_SERVICE_URL}/history/{session_id}"
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code, detail=response.json()
            )
        return response.json()
