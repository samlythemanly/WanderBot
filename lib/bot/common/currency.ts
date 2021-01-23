export const knutToGalleonRatio = 493;
export const sickleToGalleonRatio = 17;

export enum Currency {
  usd = 'usd',
  eur = 'eur',
  gbp = 'gbp',
  try = 'try',
  krw = 'krw',
  jpy = 'jpy',
  chf = 'chf',
  rub = 'rub',
  aud = 'aud',
  cad = 'cad',
  brl = 'brl',
  dkk = 'dkk',
  zar = 'zar',
  inr = 'inr',
  bdt = 'bdt',
  hkd = 'hkd',
  php = 'php',
  thb = 'thb',
  sek = 'sek',
  rsd = 'rsd',
  ars = 'ars',
  huf = 'huf',
}

export enum CurrencySymbolPosition {
  prefix,
  suffix,
}

export const formatConversion = (
  conversion: CurrencyConversion,
  value: string
) =>
  `${
    conversion.position === CurrencySymbolPosition.prefix
      ? conversion.symbol
      : ''
  }${value}${
    conversion.position === CurrencySymbolPosition.suffix
      ? ' ' + conversion.symbol
      : ''
  }`;

export const getConversion = (currency: Currency) => {
  let symbol,
    galleonRatio,
    position = CurrencySymbolPosition.prefix;

  switch (currency) {
    case Currency.usd:
      symbol = '$';
      galleonRatio = 6.64;
      break;
    case Currency.gbp:
      symbol = '£';
      galleonRatio = 4.93;
      break;
    case Currency.eur:
      symbol = '€';
      galleonRatio = 5.58;
      break;
    case Currency.try:
      symbol = '₺';
      galleonRatio = 25.98;
      break;
    case Currency.krw:
      symbol = '₩';
      galleonRatio = 7865.84;
      break;
    case Currency.jpy:
      symbol = '¥';
      galleonRatio = 744.24;
      break;
    case Currency.chf:
      symbol = 'Fr.';
      galleonRatio = 6.48;
      position = CurrencySymbolPosition.suffix;
      break;
    case Currency.rub:
      symbol = '₽';
      galleonRatio = 390.86;
      break;
    case Currency.aud:
      symbol = '$';
      galleonRatio = 8.72;
      break;
    case Currency.cad:
      symbol = '$';
      galleonRatio = 8.43;
      break;
    case Currency.brl:
      symbol = 'R$';
      galleonRatio = 21.64;
      break;
    case Currency.dkk:
      symbol = 'kr.';
      galleonRatio = 41.55;
      position = CurrencySymbolPosition.suffix;
      break;
    case Currency.zar:
      symbol = 'R ';
      galleonRatio = 91.14;
      break;
    case Currency.inr:
      symbol = '₹ ';
      galleonRatio = 428.61;
      break;
    case Currency.bdt:
      symbol = '৳';
      galleonRatio = 493;
      break;
    case Currency.hkd:
      symbol = '$';
      galleonRatio = 51.88;
      break;
    case Currency.php:
      symbol = '₱';
      galleonRatio = 333.88;
      break;
    case Currency.thb:
      symbol = '฿';
      galleonRatio = 216.61;
      break;
    case Currency.sek:
      symbol = 'kr';
      galleonRatio = 55.52;
      break;
    case Currency.rsd:
      symbol = 'RSD';
      galleonRatio = 666.58;
      position = CurrencySymbolPosition.suffix;
      break;
    case Currency.ars:
      symbol = '$';
      galleonRatio = 114.39;
      break;
    case Currency.huf:
      symbol = 'ft';
      galleonRatio = 1834;
      position = CurrencySymbolPosition.suffix;
      break;
  }

  return symbol && galleonRatio
    ? new CurrencyConversion(symbol, galleonRatio, position)
    : undefined;
};

export class CurrencyConversion {
  symbol: string;
  galleonRatio: number;
  position: CurrencySymbolPosition;

  constructor(
    symbol: string,
    galleonRatio: number,
    position: CurrencySymbolPosition
  ) {
    this.symbol = symbol;
    this.galleonRatio = galleonRatio;
    this.position = position;
  }
}
