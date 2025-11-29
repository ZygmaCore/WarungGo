const logger = require('./utils/logger');
const messageHandler = require('./messageHandler');

const normalizeNumber = (value = '') => value.replace(/[^0-9]/g, '');

const ownerNumber = normalizeNumber(process.env.OWNER_NUMBER || '');

const isOwner = (number) => {
  if (!ownerNumber) return false;
  return number === ownerNumber || number.endsWith(ownerNumber) || ownerNumber.endsWith(number);
};

const handleMessage = async (sock, message) => {
  const remoteJid = message.key.remoteJid;
  const senderJid = message.key.participant || remoteJid;
  const senderNumber = normalizeNumber(senderJid.split('@')[0]);
  const role = isOwner(senderNumber) ? 'OWNER' : 'CUSTOMER';
  console.log("DEBUG → sender:", senderNumber, "owner:", ownerNumber, "role:", role);

  try {
    await messageHandler.handle({ sock, message, jid: remoteJid, senderNumber, role });
  } catch (error) {
    logger.error({ err: error }, 'Failed to handle message');
  }
};

module.exports = {
  handleMessage
};
