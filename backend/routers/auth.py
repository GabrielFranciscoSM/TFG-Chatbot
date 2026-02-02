from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from backend.config import settings
from backend.dependencies import get_user, get_users_collection
from backend.models import Token, UserBase, UserCreate, UserInDB
from backend.security import create_access_token, get_password_hash, verify_password

router = APIRouter(tags=["auth"])


@router.post("/register", response_model=UserBase)
async def register(user: UserCreate, users_collection=Depends(get_users_collection)):
    if users_collection.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username already registered")
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user.password)
    # Exclude password and preferences (if None, let UserInDB use default)
    user_data = user.model_dump(exclude={"password", "preferences"})
    if user.preferences is not None:
        user_data["preferences"] = user.preferences.model_dump()

    user_in_db = UserInDB(**user_data, hashed_password=hashed_password)
    users_collection.insert_one(user_in_db.model_dump())
    return user_in_db


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    users_collection=Depends(get_users_collection),
):
    user = await get_user(form_data.username, users_collection)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={
            "sub": user.username,
            "role": user.role.value,
            "subjects": user.subjects,
        },
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}
