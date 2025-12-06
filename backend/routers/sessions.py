import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status

from backend.dependencies import get_current_user, get_sessions_collection
from backend.models import ChatSession, ChatSessionCreate, UserInDB, UserRole

router = APIRouter(tags=["sessions"])


@router.get("/sessions", response_model=list[ChatSession])
async def get_sessions(
    user: UserInDB = Depends(get_current_user),
    collection=Depends(get_sessions_collection),
):
    """List all chat sessions for the current user."""
    sessions = list(collection.find({"user_id": user.username}))
    return sessions


@router.post("/sessions", response_model=ChatSession)
async def create_session(
    session_in: ChatSessionCreate,
    user: UserInDB = Depends(get_current_user),
    collection=Depends(get_sessions_collection),
):
    """Create a new chat session."""

    # Verify subject enrollment (allow "general" for everyone)
    if (
        user.role == UserRole.STUDENT
        and session_in.subject != "general"
        and session_in.subject not in user.subjects
    ):
        raise HTTPException(status_code=403, detail="Not enrolled in this subject")

    session_id = str(uuid.uuid4())
    now = datetime.now(UTC)

    session_doc = {
        "_id": session_id,
        "user_id": user.username,
        "title": session_in.title,
        "subject": session_in.subject,
        "created_at": now,
        "last_active": now,
    }

    collection.insert_one(session_doc)
    return session_doc


@router.get("/sessions/{session_id}", response_model=ChatSession)
async def get_session(
    session_id: str,
    user: UserInDB = Depends(get_current_user),
    collection=Depends(get_sessions_collection),
):
    """Get details of a specific session."""
    session = collection.find_one({"_id": session_id})

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session["user_id"] != user.username:
        raise HTTPException(
            status_code=403, detail="Not authorized to access this session"
        )

    return session


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: str,
    user: UserInDB = Depends(get_current_user),
    collection=Depends(get_sessions_collection),
):
    """Delete a specific session."""
    session = collection.find_one({"_id": session_id})

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session["user_id"] != user.username:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this session"
        )

    collection.delete_one({"_id": session_id})
    return None
