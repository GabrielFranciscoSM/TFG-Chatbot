from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import admin, auth, chat, professor, sessions, users

app = FastAPI(title="TFG Chatbot Backend")

# CORS configuration for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Production frontend container
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(professor.router)
app.include_router(sessions.router)
app.include_router(chat.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
