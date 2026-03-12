from fastapi import APIRouter, Depends, HTTPException

from backend.dependencies import get_current_user, get_users_collection
from backend.models import UserBase, UserInDB, UserPreferences, UserRole

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserBase)
async def read_users_me(current_user: UserInDB = Depends(get_current_user)):
    return current_user


@router.get("/me/preferences", response_model=UserPreferences)
async def get_user_preferences(current_user: UserInDB = Depends(get_current_user)):
    """Get current user's preferences."""
    return current_user.preferences


@router.put("/me/preferences", response_model=UserPreferences)
async def update_user_preferences(
    preferences: UserPreferences,
    current_user: UserInDB = Depends(get_current_user),
    users_collection=Depends(get_users_collection),
):
    """Update current user's preferences."""
    result = users_collection.update_one(
        {"username": current_user.username},
        {"$set": {"preferences": preferences.model_dump()}},
    )

    if result.modified_count == 0 and result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return preferences


@router.get("/subject/{subject}/preferences", response_model=UserPreferences)
async def get_subject_professor_preferences(
    subject: str,
    users_collection=Depends(get_users_collection),
):
    """Get the test preferences configured by the professor of a subject.

    This endpoint is used by the chatbot to get default test configuration
    when a student requests a test for a subject.

    If multiple professors teach the subject, returns the first one's preferences.
    If no professor is found, returns default preferences.
    """
    # Find a professor who teaches this subject
    professor = users_collection.find_one(
        {
            "role": UserRole.PROFESSOR.value,
            "subjects": subject,
        }
    )

    if professor and "preferences" in professor:
        return UserPreferences(**professor["preferences"])

    # Return default preferences if no professor found or no preferences set
    return UserPreferences()
