const fs = require('fs/promises');
const path = require('path');
const { google } = require('googleapis');

const logger = require('./utils/logger');

const SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly'];
const DATA_DIR = path.join(__dirname, '..', 'data');
const MENU_PATH = path.join(DATA_DIR, 'menu.json');
const INVENTORY_PATH = path.join(DATA_DIR, 'inventory.json');
const CREDENTIALS_PATH = path.join(__dirname, '..', 'secrets', 'credentials.json');

const ensureDataDir = async () => {
  await fs.mkdir(DATA_DIR, { recursive: true });
};

const readCredentials = async () => {
  try {
    const raw = await fs.readFile(CREDENTIALS_PATH, 'utf-8');
    const parsed = JSON.parse(raw);
    if (!parsed.client_email || !parsed.private_key) {
      throw new Error('Invalid Google credentials file');
    }
    return parsed;
  } catch (error) {
    throw new Error('Unable to load Google credentials at secrets/credentials.json');
  }
};

const normalizeKey = (key = '') => key.toLowerCase().trim().replace(/\s+/g, '_');

const syncSheets = async () => {
  await ensureDataDir();

  const spreadsheetId = process.env.SHEETS_ID;
  if (!spreadsheetId) {
    throw new Error('SHEETS_ID is required for Google Sheets sync');
  }
  const range = process.env.SHEETS_RANGE || 'Menu!A2:C';

  const credentials = await readCredentials();
  const jwt = new google.auth.JWT(
    credentials.client_email,
    null,
    credentials.private_key.replace(/\\n/g, '\n'),
    SCOPES
  );

  const sheets = google.sheets({ version: 'v4', auth: jwt });
  const { data } = await sheets.spreadsheets.values.get({
    spreadsheetId,
    range
  });

  const rows = data.values || [];
  const menu = {};
  const inventory = {};

  rows.forEach((row) => {
    const [name, price, stock] = row;
    if (!name) return;
    const key = normalizeKey(name);
    menu[key] = Number(price) || 0;
    inventory[key] = Number(stock) || 0;
  });

  await fs.writeFile(MENU_PATH, JSON.stringify(menu, null, 2));
  await fs.writeFile(INVENTORY_PATH, JSON.stringify(inventory, null, 2));
  logger.info(
    { itemCount: Object.keys(menu).length },
    'Google Sheets sync completed'
  );

  return { menu, inventory };
};

module.exports = {
  syncSheets,
  MENU_PATH,
  INVENTORY_PATH
};
