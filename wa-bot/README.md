# WarungGo WhatsApp Bot

WarungGo adalah bot WhatsApp berbasis [@whiskeysockets/baileys](https://github.com/WhiskeySockets/Baileys) untuk menerima pesanan pelanggan dan membantu owner mengelola menu/stok yang disimpan di Google Sheets.

## Fitur
- Autentikasi WhatsApp Web dengan QR code dan reconnect otomatis.
- Routing pesan berdasarkan role OWNER vs CUSTOMER.
- Perintah owner: `/menu`, `/stok`, `/sync`, `/help`.
- Parsing pesan pelanggan seperti "pesan 2 indomie" dan mengirim invoice sementara.
- Sinkronisasi menu & stok dari Google Sheets ke `data/menu.json` dan `data/inventory.json`.
- Placeholder integrasi Python AI intent service via `AI_SERVICE_URL`.

## Struktur Project
```
warunggo/wa-bot/
├── src/
│   ├── index.js
│   ├── bot.js
│   ├── router.js
│   ├── messageHandler.js
│   ├── sheetsSync.js
│   ├── replyBuilder.js
│   └── utils/
│       ├── parseNumber.js
│       ├── textCleaner.js
│       └── logger.js
├── data/
│   ├── inventory.json
│   └── menu.json
├── secrets/credentials.json
├── .env.example
├── package.json
└── README.md
```

## Persiapan
1. **Install dependencies**
   ```bash
   cd warunggo/wa-bot
   npm install
   ```
2. **Buat file `.env`** berdasarkan `.env.example` lalu isi:
   - `OWNER_NUMBER`: nomor WhatsApp owner tanpa tanda `+`.
   - `BOT_NAME`: nama identitas perangkat yang tampil di WhatsApp Web.
   - `SHEETS_ID` dan `SHEETS_RANGE`: ID spreadsheet dan range (default `Menu!A2:C`).
   - `AI_SERVICE_URL` (opsional): endpoint Python AI intent service.
3. **Siapkan kredensial Google**
   - Buat Service Account di Google Cloud dan beri akses baca ke spreadsheet.
   - Unduh JSON credentials lalu simpan sebagai `secrets/credentials.json` (ganti placeholder yang ada).
   - Pastikan `private_key` masih memiliki newline `\n` (lihat contoh `.env` untuk mengganti `\n`).

## Sinkronisasi Google Sheets
Tarik menu & stok terbaru kapan saja:
```bash
npm run sync:sheets
```
Atau kirim perintah `/sync` dari WhatsApp owner. Format sheet harus `item | harga | stok`.

## Menjalankan Bot
```bash
npm start
```
- Aplikasi akan menampilkan QR code di terminal. Scan dengan aplikasi WhatsApp owner.
- Setelah tersambung, bot siap menerima pesan.

## Contoh Penggunaan
- OWNER: `/menu`, `/stok`, `/sync`, `/help`.
- CUSTOMER: kirim pesan seperti:
  - `pesan 2 indomie`
  - `beli 1 kopi hitam`
  - `mau 3 ayam_geprek`
- Pesan yang tidak dikenali akan dibalas dengan fallback dari `replyBuilder`.

## Catatan
- Data menu/inventory awal berada di folder `data/`. Jalankan `/sync` untuk menimpa dengan data dari Google Sheets.
- File `secrets/credentials.json` hanya contoh; jangan commit kredensial asli Anda.
- Placeholder integrasi AI berada di `src/messageHandler.js`. Saat Python service siap, isi `AI_SERVICE_URL` untuk mengaktifkannya.
