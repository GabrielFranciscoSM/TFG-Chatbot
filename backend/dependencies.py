from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from backend.config import settings
from backend.db.mongo import MongoDBClient
from backend.models import TokenData, UserInDB, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
mongo_client = MongoDBClient(uri=settings.MONGO_URI, db_name=settings.DB_NAME)


def get_users_collection():
    return mongo_client.get_collection("users")


async def get_user(username: str):
    users_collection = get_users_collection()
    user_dict = users_collection.find_one({"username": username})
    if user_dict:
        return UserInDB(**user_dict)
    return None


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception from None
    if token_data.username is None:
        raise credentials_exception
    user = await get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def require_admin_or_professor(user: UserInDB = Depends(get_current_user)):
    if user.role not in [UserRole.PROFESSOR, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized")
    return user
