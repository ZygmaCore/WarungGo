# WarungGo Architecture

High-level view of how the WhatsApp bot, AI microservice, Google Sheets, and Gemini LLM collaborate to automate ordering. Use alongside the `README.md` when deploying or extending the system.

---

## System Overview

```
Customer WhatsApp ↔ Baileys Socket (wa-bot)
        │                   │
        │            Owner commands (/menu, /stok, /sync)
        ▼                   ▼
   AI Chat Service (FastAPI) ───▶ Google Sheets API (sync worker)
        │
        ▼
  Gemini / LLM Provider
```

- **wa-bot/** (Node.js + Baileys): Maintains a multi-device WhatsApp session, routes inbound messages, handles QR auth, and issues owner commands.
- **ai-service/** (FastAPI + Python): Exposes `/chat`, `/parse_order`, `/invoice`, `/faq`, `/promo`, `/health` endpoints consumed by the bot and other automation.
- **Google Sheets**: Acts as the single source of truth for menu prices and inventory counts, synchronized every boot plus 5-minute intervals.
- **Gemini (via google-genai)**: Optional LLM backend to transform free text into casual replies or JSON orders.

---

## Data Flow

1. **Customer sends a message** → Baileys `messages.upsert` emits an event.
2. **Router dispatch** → `messageHandler` extracts text and either:
   - Calls the AI chat endpoint for casual replies, or
   - Runs owner command handlers to fetch menu/stok JSON.
3. **AI Service**
   - `/chat` forwards prompts to Gemini when `GEMINI_API_KEY` is set.
   - `/parse_order` first uses regex/fuzzy parsing, then falls back to Gemini for JSON extraction.
   - `/invoice` loads menu data (from Sheets sync) to compute totals and formatted strings.
4. **Sheets Sync**
   - `syncSheets()` authenticates with Google via service account credentials.
   - Normalizes rows into slugified keys and stores them in `data/menu.json` & `data/inventory.json` for quick reads.
5. **Responses** are sent back through Baileys to the WhatsApp conversation.

---

## Deployment Considerations

- **Stateful auth**: `auth_state/` must persist across restarts to avoid rescanning QR codes.
- **Environment separation**: Keep `.env` files per environment and never commit real credentials.
- **Scaling the AI service**: FastAPI can run behind `gunicorn` or `uvicorn` workers with HTTPS termination. The WhatsApp bot typically stays as a single instance due to session limits.
- **Monitoring**: `/health` endpoint and Pino logs are the primary observability tools. Consider shipping logs to a central collector if hosting remotely.

---

## Extensibility Hooks

- **Add new commands** in `wa-bot/src/messageHandler.js` or `router.js` to branch by regex or button IDs.
- **Introduce more endpoints** in `ai-service/routers/` and register them in `main.py`.
- **Swap LLM providers** by editing `utils/llm_client.py` (ensuring `ask_llm` keeps the same interface).
- **Enhance menu data** by adding more columns to Sheets and extending `sheetsSync.js` to capture them.

Stay consistent with the README conventions to keep the docs synchronized.
