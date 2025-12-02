const { aiChatService } = require('./services/aiChatService');

// Extract text from WhatsApp message
const getTextFromMessage = (msg = {}) => {
  if (!msg.message) return '';
  const c = msg.message;

  return (
    c.conversation ||
    c.extendedTextMessage?.text ||
    c.imageMessage?.caption ||
    c.videoMessage?.caption ||
    c.buttonsResponseMessage?.selectedDisplayText ||
    c.buttonsResponseMessage?.selectedButtonId ||
    c.listResponseMessage?.singleSelectReply?.selectedRowId ||
    (c.ephemeralMessage?.message && getTextFromMessage({ message: c.ephemeralMessage.message })) ||
    ''
  );
};

// Universal reply
const sendText = (sock, jid, text) => sock.sendMessage(jid, { text });

// MAIN HANDLER (ALL MESSAGES GO HERE)
const handle = async ({ sock, message, jid }) => {
  const body = getTextFromMessage(message);
  if (!body) return;

  // call AI to generate a short, casual reply
  const aiReply = await aiChatService(body);

  // kirim jawabannya
  return sendText(sock, jid, aiReply);
};

module.exports = {
  handle
};
