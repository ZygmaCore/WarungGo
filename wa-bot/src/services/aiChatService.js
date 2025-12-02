const axios = require('axios');

async function aiChatService(text) {
  const url = process.env.AI_CHAT_URL;

  if (!url) return "ga tau bro 😭 (no AI_CHAT_URL)";

  try {
    const { data } = await axios.post(url, { text });

    // ensure a reply ALWAYS exists
    if (!data || !data.reply || !data.reply.trim()) {
      return "ga tau bro 😭";
    }

    return data.reply.trim();
  } catch (err) {
    return "ga tau bro 😭";
  }
}

module.exports = { aiChatService };
