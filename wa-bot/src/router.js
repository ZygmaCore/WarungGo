const logger = require('./utils/logger');
const messageHandler = require('./messageHandler');

const handleMessage = async (sock, message) => {
  const remoteJid = message.key.remoteJid;

  try {
    await messageHandler.handle({ sock, message, jid: remoteJid });
  } catch (error) {
    logger.error({ err: error }, 'Failed to handle message');
  }
};

module.exports = {
  handleMessage
};
