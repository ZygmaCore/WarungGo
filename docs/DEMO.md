# WarungGo Demo Playbook

Use this guide to showcase WarungGo in under 10 minutes—perfect for founders, clients, or internal stakeholders.

---

## 1. Prep Checklist

- `wa-bot/.env` configured with `OWNER_NUMBER`, `BOT_NAME`, `SHEETS_ID`, `SHEETS_RANGE`, and optional `AI_CHAT_URL` pointing to `http://localhost:8000/chat`.
- `secrets/credentials.json` populated with a Google service account that can read the spreadsheet.
- AI service running locally via `uvicorn main:app --reload`.
- WhatsApp number ready to scan the QR code.

> Optional: preload demo menu data in Google Sheets (e.g., Indomie, Es Teh, Kopi) so totals look realistic.

---

## 2. Start the Services

Split your terminal into two panes.

**Pane A – FastAPI**
```bash
cd ai-service
source .venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Pane B – WhatsApp Bot**
```bash
cd wa-bot
npm start
```

Scan the QR code when prompted. Logs should show `✅ WarungGo bot berjalan` and periodic auto-sync messages.

---

## 3. Demo Flow

### Scene A – Owner Syncs Menu
1. From the owner phone, send `/sync`.
2. Terminal logs display `Google Sheets sync completed`.
3. Send `/menu` to show the formatted price list.

### Scene B – Customer Places Order
1. From another number (or same phone using a second account), send: `pesan 2 indomie goreng + 3 es teh dong`.
2. The bot forwards text to `/chat` and `/parse_order`, replies casually, and can return a structured invoice (triggered by owner command or automated flow if implemented).
3. Showcase `/invoice` endpoint response in the FastAPI docs at `http://localhost:8000/docs`.

### Scene C – FAQ & Promo
1. Ask `bisa bayar pake qris?` → Expect FAQ answer.
2. Send an order mentioning drinks twice to show the promo hint `Mau sekalian minum?`.

---

## 4. Visual Assets

Embed or screen-share these placeholders until real screenshots are captured:

![Dashboard](../assets/screenshot_1.png)
![Chat Flow](../assets/screenshot_2.png)

---

## 5. Talking Points

- **Instant onboarding**: QR code auth, no extra dashboards.
- **Live data**: Google Sheets sync every five minutes ensures accurate stock/pricing.
- **AI tone**: Casual bilingual replies from Gemini keep conversations friendly.
- **Extensibility**: Additional commands and endpoints can be added with minimal changes.

Wrap up by pointing stakeholders to the `README.md` for installation instructions and this doc for future demos.
