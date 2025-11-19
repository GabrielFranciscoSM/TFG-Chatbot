from fastapi import FastAPI

from backend.routers import admin, auth, chat, users

app = FastAPI(title="TFG Chatbot Backend")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(chat.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
