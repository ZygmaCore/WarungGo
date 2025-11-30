const fs = require('fs/promises');
const axios = require('axios');

const replyBuilder = require('./replyBuilder');
const { syncSheets, MENU_PATH, INVENTORY_PATH } = require('./sheetsSync');
const cleanText = require('./utils/textCleaner');
const parseNumber = require('./utils/parseNumber');
const logger = require('./utils/logger');

// --------------------------------------------------
// Utils
// --------------------------------------------------
const readJsonFile = async (filePath) => {
  try {
    const raw = await fs.readFile(filePath, 'utf-8');
    return JSON.parse(raw);
  } catch {
    return {};
  }
};

const loadBotData = async () => {
  const [menu, inventory] = await Promise.all([
    readJsonFile(MENU_PATH),
    readJsonFile(INVENTORY_PATH)
  ]);
  return { menu, inventory };
};

// ambil teks dari WhatsApp message
const getTextFromMessage = (msg = {}) => {
  if (!msg.message) return '';
  const m = msg.message;

  return (
    m.conversation ||
    m.extendedTextMessage?.text ||
    m.imageMessage?.caption ||
    m.videoMessage?.caption ||
    m.buttonsResponseMessage?.selectedDisplayText ||
    m.buttonsResponseMessage?.selectedButtonId ||
    m.listResponseMessage?.singleSelectReply?.selectedRowId ||
    (m.ephemeralMessage ? getTextFromMessage({ message: m.ephemeralMessage.message }) : '') ||
    ''
  );
};

// kirim pesan WA
const sendText = (sock, jid, text) => sock.sendMessage(jid, { text });

// --------------------------------------------------
// AI Calling
// --------------------------------------------------
const callAiIntentService = async (text) => {
  const endpoint = process.env.AI_SERVICE_URL;
  if (!endpoint) return null;

  try {
    const { data } = await axios.post(endpoint, { text });
    return data;
  } catch (err) {
    logger.debug({ err }, 'AI intent service unavailable');
    return null;
  }
};

// --------------------------------------------------
// Build Order dari AI-service
// --------------------------------------------------
const buildOrders = (menu, aiIntent) => {
  if (!aiIntent?.items || !Array.isArray(aiIntent.items)) {
    return [];
  }

  return aiIntent.items
    .map(({ item, qty }) => {
      if (!item) return null;

      const key = cleanText(item).replace(/\s+/g, '_');
      const quantity = Math.max(1, Number(qty) || 1);
      const price = menu[key];

      if (!price) return null;

      return {
        itemKey: key,
        quantity,
        price,
        subtotal: price * quantity
      };
    })
    .filter(Boolean);
};

// --------------------------------------------------
// Owner Commands
// --------------------------------------------------
const handleOwner = async ({ sock, jid, body }) => {
  const command = body.trim().split(' ')[0].toLowerCase();
  const { menu, inventory } = await loadBotData();

  switch (command) {
    case '/menu':
      return sendText(sock, jid, replyBuilder.buildMenu(menu));

    case '/stok':
      return sendText(sock, jid, replyBuilder.buildInventory(inventory));

    case '/sync':
      await sendText(sock, jid, '⏳ Sinkronisasi menu & stok dari Google Sheets...');
      try {
        const synced = await syncSheets();
        const output =
          replyBuilder.buildMenu(synced.menu) +
          '\n\n' +
          replyBuilder.buildInventory(synced.inventory);

        return sendText(sock, jid, output);
      } catch (err) {
        logger.error({ err }, 'Manual sync failed');
        return sendText(sock, jid, '❌ Gagal sinkronisasi. Cek credentials / koneksi.');
      }

    case '/help':
      return sendText(sock, jid, replyBuilder.buildOwnerHelp());

    default:
      return sendText(sock, jid, 'Perintah tidak dikenali. Kirim /help untuk melihat daftar perintah.');
  }
};

// --------------------------------------------------
// Customer Handler (Multi-order Support)
// --------------------------------------------------
const handleCustomer = async ({ sock, jid, senderNumber, body }) => {
  const { menu, inventory } = await loadBotData();

  if (!Object.keys(menu).length) {
    return sendText(sock, jid, 'Menu belum siap. Hubungi owner atau coba lagi nanti.');
  }

  // call AI service
  const aiIntent = await callAiIntentService(body);
  const orders = buildOrders(menu, aiIntent);

  if (!orders.length) {
    return sendText(sock, jid, replyBuilder.buildFallback());
  }

  // cek stok untuk semua item
  for (const order of orders) {
    const stock = inventory[order.itemKey] ?? 0;

    if (!stock)
      return sendText(sock, jid, `Stok ${order.itemKey.replace(/_/g, ' ')} sedang habis.`);

    if (order.quantity > stock)
      return sendText(
        sock,
        jid,
        `Stok ${order.itemKey.replace(/_/g, ' ')} tinggal ${stock}. Mohon kurangi jumlah pesanan.`
      );
  }

  // total all
  const total = orders.reduce((sum, o) => sum + o.subtotal, 0);

  const invoice = replyBuilder.buildInvoice({
    items: orders.map((o) => ({
      name: o.itemKey,
      qty: o.quantity,
      price: o.price,
      subtotal: o.subtotal
    })),
    total,
    customerNumber: `+${senderNumber}`
  });

  return sendText(sock, jid, invoice);
};

// --------------------------------------------------
// Router Entry
// --------------------------------------------------
const handle = async ({ sock, message, jid, senderNumber, role }) => {
  const body = getTextFromMessage(message);
  if (!body) return;

  if (role === 'OWNER') {
    return handleOwner({ sock, jid, body });
  }

  return handleCustomer({ sock, jid, senderNumber, body });
};

module.exports = { handle };
