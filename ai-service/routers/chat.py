from fastapi import APIRouter
from pydantic import BaseModel
from utils.llm_client import ask_llm

router = APIRouter()


class ChatRequest(BaseModel):
    text: str


@router.post("/chat")
async def chat(req: ChatRequest):
    resp = await ask_llm(f"lu jawab santai, pendek, indo-english, jaksel vibes. Pertanyaan: {req.text}")
    if not resp:
        resp = "ga tau bro 😭"
    return {"reply": resp}
