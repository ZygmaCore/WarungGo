"""Lightweight Gemini API client used as an optional LLM fallback."""

from __future__ import annotations

import os
from typing import Optional

import httpx
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
GEMINI_API_BASE = os.getenv(
    "GEMINI_API_BASE", "https://generativelanguage.googleapis.com/v1beta"
)


async def ask_llm(prompt: str) -> Optional[str]:
    """Send a prompt to Gemini and return the raw text response.

    Returns ``None`` when the integration is not configured or if the request fails.
    """

    if not GEMINI_API_KEY:
        return None

    endpoint = (
        f"{GEMINI_API_BASE.rstrip('/')}/models/{GEMINI_MODEL}:generateContent"
        f"?key={GEMINI_API_KEY}"
    )
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": (
                            "You extract structured order JSON for a warung chatbot.\n"
                            f"{prompt}"
                        )
                    }
                ],
            }
        ],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 256},
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                endpoint,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            candidates = data.get("candidates") or []
            for candidate in candidates:
                content = candidate.get("content") or {}
                parts = content.get("parts") or []
                for part in parts:
                    text = part.get("text")
                    if text:
                        return text.strip()
            return None
    except httpx.HTTPError:
        return None
