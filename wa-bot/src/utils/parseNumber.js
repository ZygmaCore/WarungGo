const textCleaner = require('./textCleaner');

const BASIC_NUMBERS = {
  nol: 0,
  kosong: 0,
  satu: 1,
  se: 1,
  dua: 2,
  tiga: 3,
  empat: 4,
  lima: 5,
  enam: 6,
  tujuh: 7,
  delapan: 8,
  lapan: 8,
  sembilan: 9,
  sepuluh: 10,
  sebelas: 11
};

const parseNumberWord = (word) => {
  if (!word) return null;
  if (BASIC_NUMBERS[word] !== undefined) {
    return BASIC_NUMBERS[word];
  }

  if (word.endsWith('belas')) {
    const prefix = word.replace('belas', '').trim();
    if (prefix === 'se') return 11;
    if (BASIC_NUMBERS[prefix] !== undefined) {
      return BASIC_NUMBERS[prefix] + 10;
    }
  }

  return null;
};

const parseNumber = (value = '') => {
  const str = value.toString();
  const numericMatch = str.match(/\d+/);
  if (numericMatch) {
    return parseInt(numericMatch[0], 10);
  }

  const cleaned = textCleaner(str);
  if (!cleaned) return null;

  const direct = parseNumberWord(cleaned);
  if (direct !== null) return direct;

  const tokens = cleaned.split(' ');
  for (let i = 0; i < tokens.length; i += 1) {
    const token = tokens[i];
    const parsed = parseNumberWord(token);
    if (parsed !== null) {
      return parsed;
    }

    if (token === 'belas' && i > 0) {
      const prev = tokens[i - 1];
      if (BASIC_NUMBERS[prev] !== undefined) {
        return BASIC_NUMBERS[prev] + 10;
      }
    }
  }

  return null;
};

module.exports = parseNumber;
