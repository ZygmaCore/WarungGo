const currency = new Intl.NumberFormat('id-ID', {
  style: 'currency',
  currency: 'IDR'
});

const title = (text) => `*${text}*`;

const buildMenu = (menu = {}) => {
  const entries = Object.entries(menu);
  if (!entries.length) {
    return `${title('Menu WarungGo')}\nBelum ada data menu. Jalankan /sync untuk menarik data dari Google Sheets.`;
  }

  const rows = entries
    .map(([name, price], index) => `${index + 1}. ${name.replace(/_/g, ' ')} — ${currency.format(price || 0)}`)
    .join('\n');

  return `${title('Menu WarungGo')}\n${rows}`;
};

const buildInventory = (inventory = {}) => {
  const entries = Object.entries(inventory);
  if (!entries.length) {
    return `${title('Stok WarungGo')}\nBelum ada data stok. Jalankan /sync terlebih dahulu.`;
  }

  const rows = entries
    .map(([name, stock], index) => `${index + 1}. ${name.replace(/_/g, ' ')} — ${stock || 0} pcs`)
    .join('\n');

  return `${title('Stok WarungGo')}\n${rows}`;
};

const buildInvoice = ({ items = [], total = 0, customerNumber }) => {
  const header = `${title('Invoice Sementara')}\nPelanggan: ${customerNumber || 'tanpa nomor'}`;
  const lines = items.map((item, index) => {
    const subtotal = item.subtotal || item.qty * item.price;
    return `${index + 1}. ${item.name.replace(/_/g, ' ')} x${item.qty} — ${currency.format(item.price)} = ${currency.format(subtotal)}`;
  });

  lines.push(`\nTotal: ${currency.format(total)}`);

  return `${header}\n${lines.join('\n')}`;
};

const buildFallback = () =>
  'Maaf, WarungGo belum paham pesanan kamu. Coba tulis seperti "pesan 2 indomie" atau minta bantuan owner.';

const buildOwnerHelp = () => {
  return `${title('Owner Commands')}\n/menu — lihat daftar menu\n/stok — lihat stok terbaru\n/sync — tarik data menu + stok dari Google Sheets\n/help — tampilkan bantuan ini`;
};

module.exports = {
  buildMenu,
  buildInventory,
  buildInvoice,
  buildFallback,
  buildOwnerHelp
};
