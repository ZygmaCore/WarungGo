"""Pydantic models for API responses."""

from typing import List

from pydantic import BaseModel, Field

from .order_model import OrderItem


class ParseOrderResponse(BaseModel):
    """Response returned by the /parse_order endpoint."""

    items: List[OrderItem] = Field(default_factory=list)
    confidence: float = Field(
        0.0, ge=0.0, le=1.0, description="Confidence score for the parsing result"
    )


class FaqResponse(BaseModel):
    """Response payload for the FAQ endpoint."""

    answer: str


class InvoiceItemResponse(OrderItem):
    """Invoice line item with pricing details."""

    unit_price: int = Field(..., ge=0)
    subtotal: int = Field(..., ge=0)


class InvoiceResponse(BaseModel):
    """Structured invoice payload for the WhatsApp bot."""

    items: List[InvoiceItemResponse] = Field(default_factory=list)
    total: int = Field(0, ge=0)
    formatted: str
