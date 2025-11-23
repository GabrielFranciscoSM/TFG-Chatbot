from fastapi import APIRouter, Depends

from backend.dependencies import get_current_user
from backend.models import UserBase, UserInDB

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserBase)
async def read_users_me(current_user: UserInDB = Depends(get_current_user)):
    return current_user
