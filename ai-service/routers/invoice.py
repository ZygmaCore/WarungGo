"""Invoice generation endpoint."""

from __future__ import annotations

import re
from typing import Dict, List

from fastapi import APIRouter
from pydantic import BaseModel, Field

from models.order_model import OrderItem
from models.response_model import InvoiceItemResponse, InvoiceResponse
from utils.price_calc import calculate_total

router = APIRouter(tags=["invoice"])


class InvoiceRequest(BaseModel):
    items: List[OrderItem] = Field(default_factory=list)
    menu: Dict[str, int] = Field(
        default_factory=dict, description="Mapping dari nama menu ke harga"
    )


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9\s]", "", text.lower())
    return re.sub(r"\s+", "_", slug).strip("_")


def _format_invoice(lines: List[dict], total: int) -> str:
    body = ["*Invoice*"]
    for idx, line in enumerate(lines, start=1):
        body.append(
            f"{idx}. {line['item']} x{line['qty']} = {line['subtotal']}"
        )
    body.append(f"Total: {total}")
    return "\n".join(body)


@router.post("/invoice", response_model=InvoiceResponse)
async def generate_invoice(payload: InvoiceRequest) -> InvoiceResponse:
    """Generate a WhatsApp-friendly invoice."""

    normalized_menu = {_slugify(name): price for name, price in payload.menu.items()}
    lines, total = calculate_total(payload.items, normalized_menu)
    formatted = _format_invoice(lines, total)
    response_items = [InvoiceItemResponse(**line) for line in lines]
    return InvoiceResponse(items=response_items, total=total, formatted=formatted)
