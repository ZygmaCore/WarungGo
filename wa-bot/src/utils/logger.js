const pino = require('pino');

const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  base: { service: 'warunggo-wa-bot' },
  timestamp: () => `,"time":"${new Date().toISOString()}"`
});

module.exports = logger;
