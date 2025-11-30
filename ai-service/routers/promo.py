"""Promo suggestions for upselling in the chat flow."""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from models.order_model import OrderItem

router = APIRouter(tags=["promo"])


class PromoRequest(BaseModel):
    items: List[OrderItem] = Field(default_factory=list)
    text: Optional[str] = Field(
        default=None, description="Optional free-form text from the user"
    )


class PromoResponse(BaseModel):
    suggestion: str


def _has_beverage(items: List[OrderItem]) -> bool:
    return any("teh" in entry.item or "kopi" in entry.item for entry in items)


def _has_main_course(items: List[OrderItem]) -> bool:
    mains = ("nasi", "ayam", "mie", "indomie")
    return any(any(keyword in entry.item for keyword in mains) for entry in items)


@router.post("/promo", response_model=PromoResponse)
async def promo_hint(payload: PromoRequest) -> PromoResponse:
    """Return a quick, rule-based promo suggestion."""

    if payload.items and not _has_beverage(payload.items):
        return PromoResponse(suggestion="Tambah es teh manis cuma 3000 aja!")

    if payload.items and _has_main_course(payload.items):
        return PromoResponse(suggestion="Paket hemat: tambah ayam geprek + es teh hanya 15000!")

    return PromoResponse(suggestion="Lagi ada promo kopi susu buy 1 get 1.")
