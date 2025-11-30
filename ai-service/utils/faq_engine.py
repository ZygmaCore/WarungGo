"""Simple FAQ engine with fuzzy matching."""

from __future__ import annotations

import re
from typing import Dict

from thefuzz import fuzz, process

FAQ_DATA: Dict[str, str] = {
    "menu": "Menu kami: indomie, nasi goreng, ayam geprek, es teh manis, kopi susu.",
    "jam buka": "WarungGo buka setiap hari dari 08.00 sampai 21.00 WIB.",
    "alamat": "Alamat WarungGo: Jl. Mawar No. 10, Jakarta.",
    "pembayaran": "Pembayaran bisa via tunai, QRIS, atau transfer bank BCA/Mandiri.",
    "delivery": "Kami bisa kirim sekitar radius 3km lewat ojek online.",
}

DEFAULT_FAQ_ANSWER = "Maaf, saya belum menemukan jawabannya. Silakan hubungi admin."
MIN_FAQ_SCORE = 60


def _normalize(text: str) -> str:
    cleaned = re.sub(r"[^a-z0-9\s]", "", text.lower())
    return re.sub(r"\s+", " ", cleaned).strip()


def get_faq_answer(question: str) -> str:
    """Return the FAQ answer that best matches the given question."""

    normalized_question = _normalize(question)
    if not normalized_question:
        return DEFAULT_FAQ_ANSWER

    choices = list(FAQ_DATA.keys())
    match = (
        process.extractOne(
            normalized_question, choices, scorer=fuzz.partial_ratio
        )
        if choices
        else None
    )
    if not match:
        return DEFAULT_FAQ_ANSWER

    key, score = match
    if score < MIN_FAQ_SCORE:
        return DEFAULT_FAQ_ANSWER

    return FAQ_DATA[key]
