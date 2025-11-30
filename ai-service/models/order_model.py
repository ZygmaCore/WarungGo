"""Pydantic models for order parsing requests."""

from pydantic import BaseModel, Field


class OrderRequest(BaseModel):
    """Incoming natural language order payload."""

    text: str = Field(..., description="Raw order text from the user")


class OrderItem(BaseModel):
    """Structured representation of an order line."""

    item: str = Field(..., description="Slugified menu item name")
    qty: int = Field(..., ge=1, description="Quantity requested")
