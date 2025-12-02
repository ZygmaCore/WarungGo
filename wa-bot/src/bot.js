const path = require('path');
const qrcode = require('qrcode-terminal');
const {
  default: makeWASocket,
  DisconnectReason,
  fetchLatestBaileysVersion,
  makeCacheableSignalKeyStore,
  useMultiFileAuthState
} = require('@whiskeysockets/baileys');

const logger = require('./utils/logger');
const router = require('./router');

const AUTH_FOLDER = path.join(__dirname, '..', 'auth_state');

const IGNORED_JID_SUFFIXES = ['@newsletter', '@broadcast'];

const shouldIgnoreJid = (jid = '') => {
  if (typeof jid !== 'string') return false;
  const ignored = IGNORED_JID_SUFFIXES.some((suffix) => jid.endsWith(suffix));
  if (ignored) {
    logger.debug({ jid }, 'Ignoring unsupported jid');
  }
  return ignored;
};

const startBot = async () => {
  const { state, saveCreds } = await useMultiFileAuthState(AUTH_FOLDER);

  const startSocket = async () => {
    const { version } = await fetchLatestBaileysVersion();
    const sock = makeWASocket({
      version,
      logger,
      printQRInTerminal: true, // QR HARUS TRUE
      auth: {
        creds: state.creds,
        keys: makeCacheableSignalKeyStore(state.keys, logger)
      },
      browser: [process.env.BOT_NAME || 'WarungGo', 'Desktop', '1.0.0'],
      shouldIgnoreJid
    });

    sock.ev.on('creds.update', saveCreds);

    sock.ev.on('connection.update', (update) => {
      const { connection, lastDisconnect, qr } = update;

      if (qr) {
        console.clear();
        qrcode.generate(qr, { small: true });
        logger.info('📲 Scan QR code to authenticate WhatsApp session...');
      }

      if (connection === 'open') {
        logger.info('✅ WhatsApp connection established');
      }

      if (connection === 'close') {
        const code =
          lastDisconnect?.error?.output?.statusCode ||
          lastDisconnect?.error?.statusCode;

        const shouldReconnect = code !== DisconnectReason.loggedOut;

        if (shouldReconnect) {
          logger.warn('⚠️ Connection closed. Reconnecting...');
          startSocket().catch((err) =>
            logger.error({ err }, 'Failed to restart socket')
          );
        } else {
          logger.error('❌ Logged out. Delete auth_state folder and restart.');
        }
      }
    });

    // Handle incoming messages
    sock.ev.on('messages.upsert', async ({ type, messages }) => {
      if (type !== 'notify') return;
      const msg = messages[0];
      if (!msg?.message || msg.key?.fromMe) return;

      await router.handleMessage(sock, msg);
    });

    return sock;
  };

  await startSocket();
};

module.exports = {
  startBot
};
