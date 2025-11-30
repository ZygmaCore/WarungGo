"""Endpoints for parsing natural language orders."""

from __future__ import annotations

import json
import re
from typing import List, Tuple

from fastapi import APIRouter
from thefuzz import process

from models.order_model import OrderItem, OrderRequest
from models.response_model import ParseOrderResponse
from utils.llm_client import ask_llm

router = APIRouter(tags=["order"])

STOP_WORDS = {"dan", "sama", "dong", "ya", "tolong", "pesan", "minta", "please"}
MENU_CATALOG = [
    "indomie",
    "indomie goreng",
    "nasi goreng",
    "ayam geprek",
    "nasi ayam",
    "nasi padang",
    "es teh manis",
    "es teh tawar",
    "teh tawar",
    "kopi susu",
    "kopi hitam",
    "jus jeruk",
    "air mineral",
]


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9\s]", "", text.lower())
    return re.sub(r"\s+", "_", slug).strip("_")


def _extract_candidates(raw_text: str) -> List[Tuple[int, str]]:
    tokens = re.findall(r"\d+|[a-zA-Z]+", raw_text.lower())
    candidates: List[Tuple[int, str]] = []
    qty = None
    buffer: List[str] = []

    def flush() -> None:
        nonlocal qty, buffer
        if qty is not None and buffer:
            candidates.append((qty, " ".join(buffer)))
        qty = None
        buffer = []

    for token in tokens:
        if token.isdigit():
            flush()
            qty = int(token)
            continue
        if qty is None or token in STOP_WORDS:
            continue
        buffer.append(token)

    flush()
    return candidates


def _match_menu_name(candidate: str) -> Tuple[str, float]:
    if not candidate:
        return "", 0.0

    match = process.extractOne(candidate, MENU_CATALOG)
    if match and match[1] >= 55:
        slug = _slugify(match[0])
        return slug, match[1] / 100

    return _slugify(candidate), 0.4


def _parse_locally(text: str) -> Tuple[List[OrderItem], float]:
    parsed_items: List[OrderItem] = []
    scores: List[float] = []

    for qty, candidate in _extract_candidates(text):
        slug, score = _match_menu_name(candidate)
        if not slug:
            continue
        parsed_items.append(OrderItem(item=slug, qty=max(1, qty)))
        scores.append(score)

    confidence = sum(scores) / len(scores) if scores else 0.0
    return parsed_items, confidence


def _extract_json_block(raw: str) -> str:
    cleaned = raw.strip()
    if cleaned.startswith("```") and cleaned.endswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()
    return cleaned


async def _parse_with_llm(text: str) -> List[OrderItem]:
    prompt = (
        "Ubah teks berikut menjadi JSON order dengan format "
        '[{"item": "name", "qty": number}]. '
        "Pastikan item dislug menjadi huruf kecil dengan underscore. "
        "Jika tidak yakin, kosongkan daftar.\n"
        f"Teks: {text}"
    )
    response = await ask_llm(prompt)
    if not response:
        return []
    try:
        payload = json.loads(_extract_json_block(response))
        items: List[OrderItem] = []
        for entry in payload:
            item = _slugify(str(entry.get("item", "")))
            qty = int(entry.get("qty", 0))
            if not item or qty <= 0:
                continue
            items.append(OrderItem(item=item, qty=qty))
        return items
    except (json.JSONDecodeError, TypeError, ValueError):
        return []


@router.post("/parse_order", response_model=ParseOrderResponse)
async def parse_order(request: OrderRequest) -> ParseOrderResponse:
    """Parse a natural language order into structured items."""

    items, confidence = _parse_locally(request.text)

    if not items:
        llm_items = await _parse_with_llm(request.text)
        if llm_items:
            items = llm_items
            confidence = 0.6

    confidence = round(min(max(confidence, 0.0), 1.0), 2)
    return ParseOrderResponse(items=items, confidence=confidence)
