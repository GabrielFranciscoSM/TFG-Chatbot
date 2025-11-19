import httpx
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from backend.config import settings

app = FastAPI(title="TFG Chatbot Backend")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    # Verify token locally or call auth service
    # For now, let's verify locally using the shared secret
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid credentials") from None


@app.post("/token")
async def login(request: Request):
    # Forward to auth service
    async with httpx.AsyncClient() as client:
        form_data = await request.form()
        # We need to pass the form data correctly
        response = await client.post(
            f"{settings.AUTH_SERVICE_URL}/token", data=form_data
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code, detail=response.json()
            )
        return response.json()


@app.post("/register")
async def register(request: Request):
    # Forward to auth service
    async with httpx.AsyncClient() as client:
        json_data = await request.json()
        response = await client.post(
            f"{settings.AUTH_SERVICE_URL}/register", json=json_data
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code, detail=response.json()
            )
        return response.json()


@app.post("/chat")
async def chat(request: Request, user: str = Depends(get_current_user)):
    # Forward to chatbot service
    # Increase timeout for chatbot response (LLM generation can be slow)
    async with httpx.AsyncClient(timeout=120.0) as client:
        json_data = await request.json()
        # Maybe inject user info into the request?
        response = await client.post(
            f"{settings.CHATBOT_SERVICE_URL}/chat", json=json_data
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code, detail=response.json()
            )
        return response.json()


@app.get("/health")
async def health():
    return {"status": "ok"}
