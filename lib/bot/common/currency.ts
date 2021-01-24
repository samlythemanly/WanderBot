export const knutToGalleonRatio = 493;
export const sickleToGalleonRatio = 17;

/**
 * Currencies that wanderbot supports.
 */
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

/**
 * Defines where currency symbols are placed when sending a value.
 *
 * i.e. $<dollars> or <francs> Fr.
 */
export enum CurrencySymbolPosition {
  prefix,
  suffix,
}

/**
 * Formats a value of currency based on its defined symbol position.
 * @param conversion The conversion object that defines the symbol position.
 * @param value The value to format.
 */
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

/**
 * Currency conversion object that defines conversion ratios and the position
 * of the currency symbol, when formatted.
 */
export class CurrencyConversion {
  symbol: string;
  galleonRatio: number;
  position: CurrencySymbolPosition;

  constructor(
    symbol: string,
    galleonRatio: number,
    position?: CurrencySymbolPosition
  ) {
    this.symbol = symbol;
    this.galleonRatio = galleonRatio;
    this.position = position ?? CurrencySymbolPosition.prefix;
  }
}

/**
 * Defines currency conversion objects, complete with conversion ratios and
 * symbol formatting positions.
 *
 * Conversion rates sourced from the following:
 * https://harrypotter.fandom.com/wiki/Wizarding_currency
 */
export const conversions = new Map<Currency, CurrencyConversion>([
  [Currency.usd, new CurrencyConversion('$', 6.64)],
  [Currency.gbp, new CurrencyConversion('£', 4.93)],
  [Currency.eur, new CurrencyConversion('€', 5.58)],
  [Currency.try, new CurrencyConversion('₺', 25.98)],
  [Currency.krw, new CurrencyConversion('₩', 7865.84)],
  [Currency.jpy, new CurrencyConversion('¥', 744.24)],
  [
    Currency.chf,
    new CurrencyConversion('Fr.', 6.48, CurrencySymbolPosition.suffix),
  ],
  [Currency.rub, new CurrencyConversion('₽', 390.86)],
  [Currency.aud, new CurrencyConversion('$', 8.72)],
  [Currency.cad, new CurrencyConversion('$', 8.43)],
  [Currency.brl, new CurrencyConversion('R$', 21.64)],
  [
    Currency.dkk,
    new CurrencyConversion('kr.', 41.55, CurrencySymbolPosition.suffix),
  ],
  [Currency.zar, new CurrencyConversion('R ', 91.14)],
  [Currency.inr, new CurrencyConversion('₹ ', 428.61)],
  [Currency.bdt, new CurrencyConversion('৳', 493)],
  [Currency.hkd, new CurrencyConversion('$', 51.88)],
  [Currency.php, new CurrencyConversion('₱', 333.88)],
  [Currency.thb, new CurrencyConversion('฿', 216.61)],
  [Currency.sek, new CurrencyConversion('kr', 55.52)],
  [
    Currency.rsd,
    new CurrencyConversion('RSD', 666.58, CurrencySymbolPosition.suffix),
  ],
  [Currency.ars, new CurrencyConversion('$', 114.39)],
  [
    Currency.huf,
    new CurrencyConversion('ft', 1834, CurrencySymbolPosition.suffix),
  ],
]);
