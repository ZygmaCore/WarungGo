"""Promo suggestions for upselling in the chat flow."""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from models.order_model import OrderItem
from models.response_model import PromoResponse

router = APIRouter(tags=["promo"])


class PromoRequest(BaseModel):
    items: List[OrderItem] = Field(default_factory=list)
    text: Optional[str] = Field(
        default=None, description="Optional free-form text from the user"
    )


BEVERAGE_KEYWORDS = ("es", "teh", "kopi", "jus", "air")


def _has_indomie(items: List[OrderItem]) -> bool:
    return any("indomie" in entry.item for entry in items)


def _beverage_qty(items: List[OrderItem]) -> int:
    total = 0
    for entry in items:
        if any(keyword in entry.item for keyword in BEVERAGE_KEYWORDS):
            total += entry.qty
    return total


@router.post("/promo", response_model=PromoResponse)
async def promo_hint(payload: PromoRequest) -> PromoResponse:
    """Return a quick, rule-based promo suggestion."""

    if payload.items and _has_indomie(payload.items):
        return PromoResponse(suggestion="Tambah telur biar lebih mantap?")

    beverage_qty = _beverage_qty(payload.items)
    if not payload.items or beverage_qty < 2:
        return PromoResponse(suggestion="Mau sekalian minum?")

    return PromoResponse(suggestion="belum ada promo")
