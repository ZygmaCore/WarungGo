"""Free-form chat endpoint backed by Gemini."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from models.response_model import ChatResponse
from utils.llm_client import ask_llm

router = APIRouter(tags=["chat"])


class ChatRequest(BaseModel):
    text: str = Field(..., description="Pesan bebas dari user")


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest) -> ChatResponse:
    """Relay chat prompt to Gemini while keeping text response."""

    prompt = (
        "Kamu adalah asisten WhatsApp WarungGo yang ramah. "
        "Jawab singkat, gunakan bahasa Indonesia santai.\n\n"
        f"User: {payload.text}"
    )
    reply = await ask_llm(prompt) or "Maaf, aku belum bisa jawab sekarang."
    return ChatResponse(reply=reply)
