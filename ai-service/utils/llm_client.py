import asyncio
import logging
import os
from typing import Optional

from google import genai
from google.genai import types

from dotenv import load_dotenv
load_dotenv()


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

_PROMPT_TEMPLATE = """
You are an AI that extracts structured JSON only.

Example output:
{
  "items": [
    { "item": "indomie", "qty": 2 },
    { "item": "es_teh", "qty": 3 }
  ]
}

Strict rules:
- ONLY output JSON.
- No explanation, no prefix, no suffix.
- No Markdown or code fences.
- If unsure, respond with {"items": []}.

User text: [[TEXT]]
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


async def ask_llm(prompt: str) -> Optional[str]:
    """
    Ask Gemini (new API) and return text output only.
    This is the *new official Google AI API style*.
    """

    client = _get_client()
    if client is None:
        logging.warning("GEMINI_API_KEY not set. Skipping LLM.")
        return None

    formatted_prompt = _PROMPT_TEMPLATE.replace("[[TEXT]]", prompt.strip())

    try:
        response = await asyncio.to_thread(
            client.models.generate_content,
            model=GEMINI_MODEL,
            contents=formatted_prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=256,
                response_mime_type="application/json",
            ),
        )
    except Exception as exc:
        logging.exception("Gemini call failed: %s", exc)
        return None

    text = (response.text or "").strip()
    if not text:
        logging.warning("Gemini returned an empty response.")
        return None

    return text
