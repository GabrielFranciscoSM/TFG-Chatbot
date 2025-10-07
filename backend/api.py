from fastapi import FastAPI
from .models import ChatRequest

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/health")
async def health():
    return {"message": "Hello World"}


@app.post("/chat")
async def chat(chat_request: ChatRequest):

    return {"query": chat_request.query, "id": chat_request.id}