import os
import logging
import asyncio
from typing import Optional

from dotenv import load_dotenv
from google import genai

load_dotenv()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
API_KEY = os.getenv("GEMINI_API_KEY")

_client: Optional[genai.Client] = None

def warmup_client():
    _get_client()
    logger.info("Gemini client warmed up.")


def _get_client():
    global _client
    if not API_KEY:
        return None
    if _client is None:
        # enforce correct API version just like Google AI Studio uses
        _client = genai.Client(
            api_key=API_KEY,
            http_options={"api_version": "v1"}   # <── FIX PALING PENTING
        )
    return _client


async def ask_llm(prompt: str) -> Optional[str]:
    client = _get_client()
    if client is None:
        logger.warning("No API key configured.")
        return None

    try:
        resp = await asyncio.to_thread(
            client.models.generate_content,
            model=GEMINI_MODEL,
            contents=[{"text": prompt}],
        )

        # Stable extraction—Google's format berubah2
        if hasattr(resp, "text") and resp.text:
            return resp.text.strip()

        if resp.candidates:
            parts = resp.candidates[0].content.parts
            for p in parts:
                if hasattr(p, "text") and p.text:
                    return p.text.strip()

        logger.warning("LLM returned empty.")
        return None

    except Exception as e:
        logger.error(f"Gemini error: {e}")
        return None
