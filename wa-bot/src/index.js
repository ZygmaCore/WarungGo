const path = require('path');
require('dotenv').config({ path: path.resolve(__dirname, '..', '.env') });

const logger = require('./utils/logger');
const { startBot } = require('./bot');
const { syncSheets } = require('./sheetsSync');

(async () => {
  try {
    logger.info('🔄 Mengambil data awal dari Google Sheets...');
    await syncSheets();

    await startBot();
    logger.info('✅ WarungGo bot berjalan');

    setInterval(async () => {
      logger.info('⏳ Auto-sync Google Sheets (interval 5 menit)...');
      try {
        await syncSheets();
        logger.info('✅ Auto-sync selesai');
      } catch (err) {
        logger.error({ err }, '❌ Auto-sync gagal');
      }
    }, 1000 * 60 * 5);

  } catch (error) {
    logger.error({ err: error }, '❌ Gagal start WarungGo');
    process.exit(1);
  }
})();
