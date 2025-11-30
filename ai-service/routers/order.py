"""Endpoints for parsing natural language orders (SAFE VERSION)."""

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

# -------------------------------
# RULES / DICTIONARIES
# -------------------------------
STOP_WORDS = {"dan", "sama", "dong", "ya", "tolong", "pesan", "minta", "please"}

MENU_CATALOG = [
    "indomie",
    "indomie goreng",
    "nasi goreng",
    "ayam geprek",
    "es teh manis",
    "es teh tawar",
    "teh tawar",
    "kopi susu",
    "kopi hitam",
    "jus jeruk",
    "air mineral",
]


# -------------------------------
# HELPERS
# -------------------------------
def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9\s]", "", text.lower())
    return re.sub(r"\s+", "_", slug).strip("_")


def _extract_candidates(raw_text: str) -> List[Tuple[int, str]]:
    """
    Extract local order pairs like "2 indomie", "3 ayam geprek".
    """
    tokens = re.findall(r"\d+|[a-zA-Z]+", raw_text.lower())

    candidates = []
    qty = None
    buffer = []

    def flush():
        nonlocal qty, buffer
        if qty and buffer:
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
    """Fuzzy match menu name against catalog."""
    if not candidate:
        return "", 0.0

    match = process.extractOne(candidate, MENU_CATALOG)

    if match and match[1] >= 55:
        return _slugify(match[0]), match[1] / 100

    # fallback: use raw slug
    return _slugify(candidate), 0.40


def _parse_locally(text: str) -> Tuple[List[OrderItem], float]:
    parsed_items = []
    scores = []

    for qty, candidate in _extract_candidates(text):
        slug, score = _match_menu_name(candidate)
        if slug:
            parsed_items.append(OrderItem(item=slug, qty=max(1, qty)))
            scores.append(score)

    confidence = sum(scores) / len(scores) if scores else 0.0
    return parsed_items, confidence


# -------------------------------
# 100% SAFE JSON EXTRACTOR
# -------------------------------
def _extract_json(text: str):
    """
    Extract JSON safely from any LLM output.
    Jupiter-tier protection.
    """
    if not text:
        return []

    # ambil substring {...} pertama
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        return []

    try:
        block = match.group(0)
        data = json.loads(block)

        # pastikan sesuai format list
        if isinstance(data, dict) and "items" in data:
            return data.get("items", [])
        if isinstance(data, list):
            return data
        return []
    except Exception:
        return []


# -------------------------------
# CALL GEMINI (WITH SAFETY)
# -------------------------------
async def _parse_with_llm(text: str) -> List[OrderItem]:
    prompt = (
        "Extract order items ONLY as JSON like: "
        '[{"item":"indomie","qty":2},{"item":"es_teh","qty":3}]. '
        "Slug all names. No words outside JSON.\n"
        f"Text: {text}"
    )

    response = await ask_llm(prompt, json_mode=True)

    if not response:
        return []

    raw_items = _extract_json(response)

    items = []
    for entry in raw_items:
        item = _slugify(str(entry.get("item", "")))
        qty = int(entry.get("qty", 0))

        if item and qty > 0:
            items.append(OrderItem(item=item, qty=qty))

    return items


# -------------------------------
# MAIN ENDPOINT
# -------------------------------
@router.post("/parse_order", response_model=ParseOrderResponse)
async def parse_order(request: OrderRequest) -> ParseOrderResponse:

    # Step 1: local parser
    items, confidence = _parse_locally(request.text)
    if items and confidence < 0.4:
        confidence = 0.4

    # Step 2: fallback LLM only if no local match
    if not items:
        llm_items = await _parse_with_llm(request.text)
        if llm_items:
            items = llm_items
            confidence = 0.9  # LLM baseline confidence

    return ParseOrderResponse(
        items=items,
        confidence=round(max(min(confidence, 1.0), 0.0), 2),
    )
