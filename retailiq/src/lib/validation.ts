import type { Transaction, DataQualityReport, DataQualityIssue } from './types';

const REQUIRED_COLUMNS = [
  'transaction_id', 'transaction_date', 'customer_id', 'sales_amount',
  'product_id', 'category', 'quantity', 'unit_price',
];

export function validateSchema(headers: string[]): { valid: boolean; missing: string[]; extra: string[] } {
  const headerSet = new Set(headers.map((h) => h.toLowerCase().trim()));
  const missing = REQUIRED_COLUMNS.filter((c) => !headerSet.has(c.toLowerCase()));
  const extra = headers.filter((h) => !REQUIRED_COLUMNS.some((c) => c.toLowerCase() === h.toLowerCase().trim()));
  return { valid: missing.length === 0, missing, extra };
}

export function detectDataQuality(data: Transaction[]): DataQualityReport {
  const issues: DataQualityIssue[] = [];
  let totalIssues = 0;

  // Missing values per column
  const columns: (keyof Transaction)[] = ['transaction_id', 'transaction_date', 'customer_id', 'sales_amount', 'quantity', 'unit_price', 'category', 'customer_name'];
  columns.forEach((col) => {
    const count = data.filter((r) => r[col] === null || r[col] === undefined || r[col] === '').length;
    if (count > 0) {
      issues.push({ type: `Missing ${String(col)}`, count, severity: ['transaction_id', 'customer_id', 'sales_amount'].includes(String(col)) ? 'high' : 'medium', description: `${count} rows have missing ${String(col)}` });
      totalIssues += count;
    }
  });

  // Duplicates
  const idCounts = new Map<string, number>();
  data.forEach((r) => idCounts.set(r.transaction_id, (idCounts.get(r.transaction_id) || 0) + 1));
  const dupes = Array.from(idCounts.values()).filter((c) => c > 1).reduce((a, b) => a + b - 1, 0);
  if (dupes > 0) {
    issues.push({ type: 'Duplicate Transactions', count: dupes, severity: 'high', description: `${dupes} duplicate transaction IDs found` });
    totalIssues += dupes;
  }

  // Invalid dates
  const invalidDates = data.filter((r) => {
    const d = new Date(r.transaction_date);
    return isNaN(d.getTime()) || r.transaction_date.includes('00') || r.transaction_date.includes('13');
  }).length;
  if (invalidDates > 0) {
    issues.push({ type: 'Invalid Dates', count: invalidDates, severity: 'high', description: `${invalidDates} rows have unparseable or invalid dates` });
    totalIssues += invalidDates;
  }

  // Negative quantities
  const negQty = data.filter((r) => r.quantity < 0).length;
  if (negQty > 0) {
    issues.push({ type: 'Negative Quantities', count: negQty, severity: 'high', description: `${negQty} rows have negative quantity values` });
    totalIssues += negQty;
  }

  // Zero prices
  const zeroPrice = data.filter((r) => r.unit_price === 0).length;
  if (zeroPrice > 0) {
    issues.push({ type: 'Zero Prices', count: zeroPrice, severity: 'medium', description: `${zeroPrice} rows have unit_price of 0` });
    totalIssues += zeroPrice;
  }

  // Extreme outliers
  const prices = data.map((r) => r.unit_price).filter((v) => typeof v === 'number' && v > 0);
  const mean = prices.reduce((a, b) => a + b, 0) / prices.length;
  const std = Math.sqrt(prices.reduce((a, b) => a + (b - mean) ** 2, 0) / prices.length);
  const outliers = data.filter((r) => Math.abs(r.unit_price - mean) > 3 * std).length;
  if (outliers > 0) {
    issues.push({ type: 'Price Outliers', count: outliers, severity: 'medium', description: `${outliers} rows with unit_price > 3 standard deviations from mean` });
    totalIssues += outliers;
  }

  // High discounts
  const highDiscount = data.filter((r) => r.discount_percent > 80).length;
  if (highDiscount > 0) {
    issues.push({ type: 'Unusually High Discounts', count: highDiscount, severity: 'low', description: `${highDiscount} rows with discount > 80%` });
    totalIssues += highDiscount;
  }

  const validRows = data.length - totalIssues;
  return { totalRows: data.length, validRows: Math.max(0, validRows), issues };
}

export function cleanData(data: Transaction[], options: { removeDuplicates?: boolean; removeInvalidDates?: boolean; removeNegativeQty?: boolean; removeZeroPrice?: boolean } = {}): Transaction[] {
  let result = [...data];

  if (options.removeDuplicates !== false) {
    const seen = new Set<string>();
    result = result.filter((r) => {
      if (seen.has(r.transaction_id)) return false;
      seen.add(r.transaction_id);
      return true;
    });
  }

  if (options.removeInvalidDates !== false) {
    result = result.filter((r) => {
      const d = new Date(r.transaction_date);
      return !isNaN(d.getTime());
    });
  }

  if (options.removeNegativeQty !== false) {
    result = result.filter((r) => r.quantity >= 0);
  }

  if (options.removeZeroPrice !== false) {
    result = result.filter((r) => r.unit_price > 0);
  }

  return result;
}
