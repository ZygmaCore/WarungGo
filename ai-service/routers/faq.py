"""FAQ endpoint backed by a simple rule-based engine."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from models.response_model import FaqResponse
from utils.faq_engine import get_faq_answer

router = APIRouter(tags=["faq"])


class FaqRequest(BaseModel):
    question: str = Field(..., description="Pertanyaan dari pengguna")


@router.post("/faq", response_model=FaqResponse)
async def answer_faq(payload: FaqRequest) -> FaqResponse:
    """Return an FAQ answer for the given user question."""

    answer = get_faq_answer(payload.question)
    return FaqResponse(answer=answer)
