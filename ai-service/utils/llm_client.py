"""Google Gemini client helpers."""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Optional

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

_JSON_PROMPT_TEMPLATE = """
Kamu adalah AI ekstraksi pesanan. Jawab HANYA JSON valid.

Contoh:
{{
  "items": [
    {{ "item": "indomie", "qty": 2 }},
    {{ "item": "es_teh", "qty": 3 }}
  ]
}}

Aturan:
- Tidak boleh ada teks lain di luar JSON.
- Jika tidak paham, jawab {{ "items": [] }}.
- Gunakan snake_case/slug.

Teks pengguna: [[TEXT]]
"""

_client: Optional[genai.Client] = None


def _get_client() -> Optional[genai.Client]:
    """Create a Gemini client when an API key is available."""

    global _client
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    if _client is None:
        _client = genai.Client(api_key=api_key)
    return _client


def warmup_client() -> None:
    """Initialize Gemini client if credentials are available."""

    if _get_client() is not None:
        logger.info("Gemini client initialized.")


def reset_client() -> None:
    """Dispose the cached client (best-effort)."""

    global _client
    _client = None


def _format_prompt(prompt: str, json_mode: bool) -> str:
    if json_mode:
        return _JSON_PROMPT_TEMPLATE.replace("[[TEXT]]", prompt.strip())
    return prompt.strip()


async def ask_llm(prompt: str, *, json_mode: bool = False) -> Optional[str]:
    """
    Ask Gemini (new API) and return the generated text.

    When json_mode=True, a strict template and JSON mime type are enforced.
    """

    if not prompt or not prompt.strip():
        return None

    client = _get_client()
    if client is None:
        logger.warning("GEMINI_API_KEY not set. Skipping LLM.")
        return None

    formatted_prompt = _format_prompt(prompt, json_mode)
    mime_type = "application/json" if json_mode else "text/plain"

    try:
        response = await asyncio.to_thread(
            client.models.generate_content,
            model=GEMINI_MODEL,
            contents=formatted_prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=256,
                response_mime_type=mime_type,
            ),
        )
    except Exception as exc:
        logger.exception("Gemini call failed: %s", exc)
        return None

    text = (response.text or "").strip() if response else ""
    if not text:
        logger.warning("Gemini returned an empty response.")
        return None

    return text
