"""Simple FAQ engine with fuzzy matching."""

from __future__ import annotations

import re
from typing import Dict

from thefuzz import process

FAQ_DATA: Dict[str, str] = {
    "menu": "Menu kami: indomie, nasi goreng, ayam geprek, es teh manis, kopi susu.",
    "jam buka": "Warung buka setiap hari dari pukul 08.00 sampai 21.00 WIB.",
    "alamat": "Warung Go beralamat di Jl. Mawar No. 10, Jakarta.",
}

DEFAULT_FAQ_ANSWER = "Maaf, saya belum menemukan jawabannya. Silakan hubungi admin."


def _normalize(text: str) -> str:
    cleaned = re.sub(r"[^a-z0-9\s]", "", text.lower())
    return re.sub(r"\s+", " ", cleaned).strip()


def get_faq_answer(question: str) -> str:
    """Return the FAQ answer that best matches the given question."""

    normalized_question = _normalize(question)
    if not normalized_question:
        return DEFAULT_FAQ_ANSWER

    choices = list(FAQ_DATA.keys())
    match = process.extractOne(normalized_question, choices) if choices else None
    if not match:
        return DEFAULT_FAQ_ANSWER

    key, score = match
    if score < 60:
        return DEFAULT_FAQ_ANSWER

    return FAQ_DATA[key]
