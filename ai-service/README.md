# WarungGo AI Service

FastAPI-based microservice that powers the WhatsApp bot's AI features. It parses natural language orders, answers common questions, builds invoices, and suggests simple promos.

## Features
- `/parse_order`: Regex + fuzzy matching (with optional Gemini fallback) to convert free-text orders into structured JSON lines with confidence scores.
- `/faq`: Lightweight FAQ engine backed by `thefuzz` to match user questions against predefined answers.
- `/invoice`: Generates totals and WhatsApp-friendly invoice text using `price_calc` utilities.
- `/promo`: Optional rule-based upsell suggestions tailored to the ordered items.
- `/health`: Basic health check endpoint for monitoring.

## Project Structure
```
ai-service/
  main.py            # FastAPI entrypoint & router registration
  routers/           # HTTP endpoints
  models/            # Pydantic schemas for requests & responses
  utils/             # LLM client, FAQ engine, price calculator
  requirements.txt   # Minimal runtime dependencies
```

## Getting Started
```bash
cd ai-service
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```
Service runs at http://127.0.0.1:8000 by default. Interactive docs available at `/docs`.

## Environment Variables (Optional)
- `GEMINI_API_KEY`: Enables Gemini LLM fallback for order parsing.
- `GEMINI_API_BASE`: Override the default Gemini endpoint base URL.
- `GEMINI_MODEL`: Model name (defaults to `gemini-1.5-flash`).

Without these variables the service still works, falling back to rule-based parsing.

## Example Requests
### Parse Order
```bash
curl -X POST http://localhost:8000/parse_order \
  -H "Content-Type: application/json" \
  -d '{"text": "pesan 2 indomie 3 es teh manis"}'
```

### FAQ
```bash
curl -X POST http://localhost:8000/faq \
  -H "Content-Type: application/json" \
  -d '{"question": "jam buka warung kapan"}'
```

### Invoice
```bash
curl -X POST http://localhost:8000/invoice \
  -H "Content-Type: application/json" \
  -d '{
        "items": [
          {"item": "indomie", "qty": 2},
          {"item": "es_teh_manis", "qty": 3}
        ],
        "menu": {"indomie": 3000, "es_teh_manis": 4000}
      }'
```

## Testing & Linting
No formal test suite yet. Suggested next step is to add unit tests for the parsers and utilities using `pytest`.

## Deployment
- Run via `uvicorn main:app --host 0.0.0.0 --port 8000` for production.
- Keep `requirements.txt` in sync with dependencies installed to the runtime image.

Happy hacking!
