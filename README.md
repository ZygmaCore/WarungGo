<h1 align="center">WarungGo</h1>

<p align="center">
  <img src="https://img.shields.io/badge/license-MIT-blue.svg" />
  <img src="https://img.shields.io/badge/language-Node.js%20%26%20Python-blue.svg" />
  <img src="https://img.shields.io/badge/status-active-brightgreen.svg" />
</p>

<p align="center">
  <img src="assets/zygmacore.jpeg" alt="Logo" width="180">
</p>

<h3 align="center">
  WhatsApp-native assistant that syncs your menu from Google Sheets and responds with AI flair.
</h3>

---

## 📘 About The Project

WarungGo is a dual-service toolkit that blends a Baileys-powered WhatsApp bot with a FastAPI AI microservice and a Google Sheets sync worker so micro-merchants can automate ordering without new hardware.

**Highlights**
- 24/7 WhatsApp bot built on Baileys multi-device sessions.
- FastAPI AI endpoints for chat replies, order parsing, invoices, and promo hints.
- Service-account Google Sheets sync for live menu and stock visibility.

**Built for**
- Warung and micro-merchant owners who live in WhatsApp.
- Agencies or startup teams prototyping conversational commerce flows.
- Developers that need a reference stack for chat-based ordering assistants.

---

### 💡 Why This Project Exists

**Problems solved**
- Manual WhatsApp order triage that delays responses and causes mistakes.
- Menu & stock numbers drifting between spreadsheets and actual chats.
- Owner fatigue from repeating FAQs and calculating totals in their head.

**Goals we keep chasing**
- Deliver a casual bilingual bot voice that feels natural to customers.
- Keep infrastructure lightweight—just WhatsApp Web plus Google Sheets.
- Provide extensible code so new commands or AI models plug in quickly.

---

## 🖼 Screenshot

![Screenshot](assets/screenshot_1.png)
![Screenshot](assets/screenshot_2.png)

---

## 🛠 Tech Stack

| Technology | Usage |
| --- | --- |
| Node.js + Baileys | WhatsApp multi-device gateway, routing, and QR-based auth |
| FastAPI (Python) | AI microservice powering chat, parse_order, invoice, FAQ, and promo endpoints |
| Google Sheets API | Menu & inventory synchronization through a service-account worker |

---

## ✨ Key Features

- QR onboarding, multi-file auth state, and auto-reconnect keep the bot online 24/7.
- Scheduled Google Sheets sync normalizes menu items into JSON for quick lookups.
- FastAPI chat endpoint proxies Gemini for Jaksel-vibe replies when `AI_CHAT_URL` is set.
- Rule-based + LLM hybrid order parser outputs clean JSON lines for invoices.
- WhatsApp-friendly invoice builder formats Rupiah totals and customer context.
- FAQ and promo micro-engines deflect repetitive questions and nudge upsells.

---

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ and npm.
- Python 3.10+ with `uvicorn`, FastAPI, and a virtual environment tool (venv/pyenv).
- A WhatsApp number you control, Google Cloud service-account credentials for Sheets, and optional Gemini API keys.

### Installation

```bash
git clone https://github.com/ZygmaCore/warunggo.git
cd warunggo
cd wa-bot && npm install
cd ../ai-service
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Configure `wa-bot/.env` (see `.env.example`), place `secrets/credentials.json`, and export Gemini variables for the AI service when needed.

### ▶️ Usage

1. Start the AI microservice:

```bash
cd ai-service
source .venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

2. In a new terminal, fire up the WhatsApp bot from the `wa-bot/` folder:

```bash
npm start
```

After scanning the QR code, the bot will auto-sync Sheets every five minutes while routing inbound chats through the AI endpoint defined by `AI_CHAT_URL`.

#### Example Output

```text
> npm start
🔄 Mengambil data awal dari Google Sheets...
✅ WarungGo bot berjalan
⏳ Auto-sync Google Sheets (interval 5 menit)...
```

---

## 🤝 Contributing

- Fork the repo, create a feature branch, and keep changes scoped.
- Run linting/tests for both `wa-bot` and `ai-service` before opening a PR.
- Describe context, screenshots/logs, and configuration updates in the pull request.

---

## 📄 License & Contact

Released under the MIT License — see `LICENSE` for details.

Connect with the author:
- https://alhikam.me
- https://github.com/ZygmaCore

Happy building!
