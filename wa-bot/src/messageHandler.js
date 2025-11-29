const fs = require('fs/promises');
const axios = require('axios');

const replyBuilder = require('./replyBuilder');
const { syncSheets, MENU_PATH, INVENTORY_PATH } = require('./sheetsSync');
const parseNumber = require('./utils/parseNumber');
const cleanText = require('./utils/textCleaner');
const logger = require('./utils/logger');

const ACTION_WORDS = new Set(['pesan', 'beli', 'mau', 'order', 'ambil', 'tolong', 'ingin', 'minta', 'saya', 'aku', 'gue', 'dong']);

const readJsonFile = async (filePath) => {
  try {
    const raw = await fs.readFile(filePath, 'utf-8');
    return JSON.parse(raw);
  } catch (error) {
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

const getTextFromMessage = (msg = {}) => {
  if (!msg.message) return '';
  const messageContent = msg.message;
  if (messageContent.conversation) return messageContent.conversation;
  if (messageContent.extendedTextMessage?.text) return messageContent.extendedTextMessage.text;
  if (messageContent.imageMessage?.caption) return messageContent.imageMessage.caption;
  if (messageContent.videoMessage?.caption) return messageContent.videoMessage.caption;
  if (messageContent.buttonsResponseMessage?.selectedDisplayText) {
    return messageContent.buttonsResponseMessage.selectedDisplayText;
  }
  if (messageContent.buttonsResponseMessage?.selectedButtonId) {
    return messageContent.buttonsResponseMessage.selectedButtonId;
  }
  if (messageContent.listResponseMessage?.singleSelectReply?.selectedRowId) {
    return messageContent.listResponseMessage.singleSelectReply.selectedRowId;
  }
  if (messageContent.ephemeralMessage?.message) {
    return getTextFromMessage({ message: messageContent.ephemeralMessage.message });
  }
  return '';
};

const sendText = (sock, jid, text) => sock.sendMessage(jid, { text });

const findItemKey = (cleanedText, menuKeys) => {
  if (!cleanedText) return null;
  const slug = cleanedText.replace(/\s+/g, '_');
  let match = menuKeys.find((key) => slug.includes(key));
  if (match) return match;

  const tokens = cleanedText.split(' ').filter(Boolean);
  const filtered = tokens.filter((token) => !ACTION_WORDS.has(token) && Number.isNaN(Number(token)));

  match = filtered
    .map((token) => menuKeys.find((key) => key.includes(token)))
    .filter(Boolean)[0];
  if (match) return match;

  for (let size = filtered.length; size > 0; size -= 1) {
    for (let start = 0; start <= filtered.length - size; start += 1) {
      const slice = filtered.slice(start, start + size).join('_');
      match = menuKeys.find((key) => key.includes(slice));
      if (match) return match;
    }
  }

  return null;
};

const buildOrder = (text, menu, aiIntent) => {
  if (!text || !Object.keys(menu).length) return null;
  const cleaned = cleanText(text);
  if (!cleaned) return null;

  let quantity = aiIntent?.qty ? Number(aiIntent.qty) : null;
  if (!quantity || Number.isNaN(quantity)) {
    quantity = parseNumber(text) || 1;
  }

  let itemKey = aiIntent?.item ? cleanText(aiIntent.item).replace(/\s+/g, '_') : null;
  if (!itemKey) {
    itemKey = findItemKey(cleaned, Object.keys(menu));
  }

  if (!itemKey || !menu[itemKey]) return null;

  return { itemKey, quantity: Math.max(1, quantity) };
};

const callAiIntentService = async (text) => {
  // TODO: integrate Python AI intent service for smarter understanding
  const endpoint = process.env.AI_SERVICE_URL;
  if (!endpoint) return null;

  try {
    const { data } = await axios.post(endpoint, { text });
    return data;
  } catch (error) {
    logger.debug({ err: error }, 'AI intent placeholder unavailable');
    return null;
  }
};

const handleOwner = async ({ sock, jid, body }) => {
  const command = body.trim().split(' ')[0].toLowerCase();
  const { menu, inventory } = await loadBotData();

  switch (command) {
    case '/menu':
      return sendText(sock, jid, replyBuilder.buildMenu(menu));
    case '/stok':
      return sendText(sock, jid, replyBuilder.buildInventory(inventory));
    case '/sync': {
      await sendText(sock, jid, '⏳ Sinkronisasi menu & stok dari Google Sheets...');
      try {
        const synced = await syncSheets();
        const response = `${replyBuilder.buildMenu(synced.menu)}\n\n${replyBuilder.buildInventory(synced.inventory)}`;
        return sendText(sock, jid, response);
      } catch (error) {
        logger.error({ err: error }, 'Manual sync failed');
        return sendText(sock, jid, '❌ Gagal sinkronisasi. Cek credentials dan koneksi lalu coba lagi.');
      }
    }
    case '/help':
      return sendText(sock, jid, replyBuilder.buildOwnerHelp());
    default:
      return sendText(sock, jid, 'Perintah tidak dikenali. Kirim /help untuk melihat daftar perintah owner.');
  }
};

const handleCustomer = async ({ sock, jid, senderNumber, body }) => {
  const { menu, inventory } = await loadBotData();
  if (!Object.keys(menu).length) {
    return sendText(sock, jid, 'Menu belum siap. Silakan hubungi owner atau coba lagi nanti.');
  }

  const aiIntent = await callAiIntentService(body);
  const order = buildOrder(body, menu, aiIntent);
  if (!order) {
    return sendText(sock, jid, replyBuilder.buildFallback());
  }

  const price = menu[order.itemKey];
  const stock = inventory[order.itemKey] ?? 0;
  if (!stock) {
    return sendText(sock, jid, `Stok ${order.itemKey.replace(/_/g, ' ')} sedang habis. Coba menu lain ya!`);
  }

  if (order.quantity > stock) {
    return sendText(
      sock,
      jid,
      `Stok ${order.itemKey.replace(/_/g, ' ')} tinggal ${stock} porsi. Mohon sesuaikan jumlah pesananmu.`
    );
  }

  const subtotal = price * order.quantity;
  const invoice = replyBuilder.buildInvoice({
    items: [
      {
        name: order.itemKey,
        qty: order.quantity,
        price,
        subtotal
      }
    ],
    total: subtotal,
    customerNumber: senderNumber ? `+${senderNumber}` : undefined
  });

  return sendText(sock, jid, invoice);
};

const handle = async ({ sock, message, jid, senderNumber, role }) => {
  const body = getTextFromMessage(message);
  if (!body) return null;

  if (role === 'OWNER') {
    return handleOwner({ sock, jid, body });
  }

  return handleCustomer({ sock, jid, senderNumber, body });
};

module.exports = {
  handle
};
