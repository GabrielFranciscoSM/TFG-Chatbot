from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from backend.logging_config import CorrelationIdMiddleware, setup_logging
from backend.routers import admin, auth, chat, professor, sessions, subjects, users

# Initialize structured logging
setup_logging()

app = FastAPI(title="TFG Chatbot Backend")

# Initialize Prometheus instrumentator
Instrumentator().instrument(app).expose(app)

# Add correlation ID middleware
app.add_middleware(CorrelationIdMiddleware)

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
app.include_router(subjects.router)
app.include_router(subjects.public_router)
app.include_router(professor.router)
app.include_router(sessions.router)
app.include_router(chat.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
