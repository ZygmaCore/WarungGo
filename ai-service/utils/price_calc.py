"""Utility helpers for composing invoice totals."""

from __future__ import annotations

from typing import Dict, List, Tuple

from models.order_model import OrderItem


def calculate_total(
    items: List[OrderItem], menu: Dict[str, int]
) -> Tuple[List[dict], int]:
    """Calculate per-item subtotals and the grand total.

    Args:
        items: Structured list of order items.
        menu: Mapping of slugified menu names to unit prices.

    Returns:
        Tuple containing the enriched line items and the total cost.
    """

    detailed_items = []
    total = 0

    for entry in items:
        unit_price = int(menu.get(entry.item, 0))
        subtotal = unit_price * entry.qty
        detailed_items.append(
            {
                "item": entry.item,
                "qty": entry.qty,
                "unit_price": unit_price,
                "subtotal": subtotal,
            }
        )
        total += subtotal

    return detailed_items, total
