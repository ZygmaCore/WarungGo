# WarungGo Feature Brief

Snapshot of the most important capabilities, who they help, and the value they unlock.

---

## Personas 🎯
- **Warung Owners** who rely on WhatsApp to accept and confirm daily orders.
- **Ops/Agency Teams** prototyping conversational commerce experiences for clients.
- **Developers** seeking a ready-made reference stack that ties Baileys, FastAPI, and Google Sheets together.

---

## Problems We Solve 🧩
1. Manual WhatsApp triage causing slow replies and missed revenue.
2. Spreadsheet menus drifting out of sync with actual inventory shared in chat.
3. Repetitive FAQs and mental math draining owners’ energy.

---

## Strategic Goals 🎯
1. Keep infrastructure lightweight so merchants only manage WhatsApp + Google Sheets.
2. Deliver natural Jaksel-style responses that feel personal yet automated.
3. Provide an extensible foundation for new commands, channels, or AI providers.

---

## Core Features ✨
- **AI Chat Relay**: `/chat` endpoint proxies Gemini to craft short bilingual replies.
- **Hybrid Order Parser**: Regex + fuzzy matching backed by safe LLM extraction for JSON accuracy.
- **WhatsApp Invoice Builder**: Formats Rupiah totals and customer context in bold-friendly text.
- **Google Sheets Sync Worker**: Service-account integration that normalizes menu + inventory into JSON files.
- **Owner Command Suite**: `/menu`, `/stok`, `/sync`, `/help` keep human operators in control.
- **Promo & FAQ Micro-engines**: Simple rule bases turn structured items into upsells or instant answers.

---

## Tech Stack Highlights 🛠
| Layer | Technology | Reason |
| --- | --- | --- |
| Messaging | Node.js + @whiskeysockets/baileys | Stable multi-device WhatsApp sessions with QR auth |
| AI Service | FastAPI + Google genai SDK | Async endpoints, easy deployment, Gemini integration |
| Data | Google Sheets API | Owner-friendly source of truth for menus and inventory |

---

## Success Metrics 📏
- Response time to new WhatsApp messages < 5s (bot auto-replies before owner intervenes).
- Menu/stock accuracy, measured by successful `/sync` events every 5 minutes.
- Reduction of repetitive FAQ replies by >50% once `/faq` routing is enabled.

For deeper implementation details, check `README.md`, `docs/API.md`, and `docs/ARCHITECTURE.md`.
