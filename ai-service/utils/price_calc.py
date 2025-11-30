"""Utility helpers for composing invoice totals."""

from __future__ import annotations

from typing import Dict, List, Tuple

from models.order_model import OrderItem

DEFAULT_MENU_PRICES: Dict[str, int] = {
    "indomie": 3500,
    "indomie_goreng": 5000,
    "nasi_goreng": 12000,
    "ayam_geprek": 15000,
    "es_teh": 3000,
    "es_teh_manis": 3000,
    "es_teh_tawar": 2500,
    "kopi_susu": 8000,
    "kopi_hitam": 6000,
    "jus_jeruk": 10000,
    "air_mineral": 4000,
}


def format_rupiah(amount: int) -> str:
    """Return Rupiah formatted with dots."""

    return f"Rp{amount:,.0f}".replace(",", ".")


def calculate_total(
    items: List[OrderItem],
    menu: Dict[str, int] | None = None,
) -> Tuple[List[dict], int]:
    """Calculate per-item subtotals and the grand total."""

    price_catalog = DEFAULT_MENU_PRICES.copy()
    if menu:
        price_catalog.update({key: int(value) for key, value in menu.items()})

    detailed_items = []
    total = 0

    for entry in items:
        unit_price = int(price_catalog.get(entry.item, 0))
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
