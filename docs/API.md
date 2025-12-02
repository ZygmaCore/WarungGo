# WarungGo API Reference

Comprehensive overview of the FastAPI-based AI service plus the WhatsApp bot command surface. Use this doc with the root `README.md` to integrate the services smoothly.

---

## Base URLs

| Service | Description | Default URL |
| --- | --- | --- |
| AI Service (FastAPI) | Handles chat replies, order parsing, invoice generation, FAQ, promo hints, and health checks. | `http://localhost:8000` |
| WhatsApp Bot (Baileys) | Listens for WhatsApp messages and calls the AI service via `AI_CHAT_URL`. | runs locally via `npm start` |

> Set `AI_CHAT_URL` in `wa-bot/.env` to point at the `/chat` endpoint (e.g., `http://localhost:8000/chat`).

---

## REST Endpoints (FastAPI)

### `POST /chat`
Free-form chat endpoint that wraps Gemini to produce short Jaksel-style responses.

**Request**
```json
{
  "text": "lagi buka jam berapa?"
}
```

**Response**
```json
{
  "reply": "buka sampe malem kok, santai aja"
}
```

### `POST /parse_order`
Parses natural-language orders using regex/fuzzy logic with optional LLM fallback.

**Request**
```json
{
  "text": "pesan 2 indomie goreng sama 3 es teh"
}
```

**Response**
```json
{
  "items": [
    { "item": "indomie_goreng", "qty": 2 },
    { "item": "es_teh", "qty": 3 }
  ],
  "confidence": 0.88
}
```

### `POST /invoice`
Calculates totals and returns WhatsApp-ready invoice text.

**Request**
```json
{
  "items": [
    { "item": "indomie", "qty": 2 },
    { "item": "es_teh", "qty": 3 }
  ],
  "menu": {
    "indomie": 3500,
    "es_teh": 3000
  }
}
```

**Response**
```json
{
  "items": [
    { "item": "indomie", "qty": 2, "unit_price": 3500, "subtotal": 7000 },
    { "item": "es_teh", "qty": 3, "unit_price": 3000, "subtotal": 9000 }
  ],
  "total": 16000,
  "formatted": "*Invoice*\n1. Indomie x2 - Rp3.500 = Rp7.000\n2. Es Teh x3 - Rp3.000 = Rp9.000\nTotal: Rp16.000"
}
```

### `POST /faq`
Returns canned answers to popular questions (hours, delivery, payment).

**Request**
```json
{
  "question": "bisa bayar pake qris?"
}
```

**Response**
```json
{
  "answer": "Bisa, tinggal kirim bukti bayar QRIS ya."
}
```

### `POST /promo`
Rule-based upsell suggestions given structured items.

**Request**
```json
{
  "items": [
    { "item": "indomie", "qty": 1 }
  ]
}
```

**Response**
```json
{
  "suggestion": "Tambah telur biar lebih mantap?"
}
```

### `GET /health`
Simple heartbeat endpoint.

**Response**
```json
{ "status": "ok" }
```

---

## WhatsApp Bot Commands

While most flows are automated, owner-only commands remain available via WhatsApp:

| Command | Access | Description |
| --- | --- | --- |
| `/menu` | Owner | Sends the latest menu from `data/menu.json`. |
| `/stok` | Owner | Shares current inventory counts. |
| `/sync` | Owner | Triggers Google Sheets sync immediately. |
| `/help` | Owner | Lists available owner commands. |

Customer chats are routed automatically. Anything unrecognized can be forwarded to `/chat` for AI replies if `AI_CHAT_URL` is configured.

---

## Error Handling Tips

- **Missing AI key**: `/chat` will return `ga tau bro 😭`. Ensure Gemini variables are set and reachable.
- **Sheets sync failure**: WhatsApp bot logs will show `Unable to load Google credentials`. Verify `secrets/credentials.json`.
- **LLM JSON parsing**: `/parse_order` enforces safe JSON extraction; invalid responses simply fall back to rule-based parsing with lower confidence.

Need more? Open an issue or ping `@ZygmaCore`.
