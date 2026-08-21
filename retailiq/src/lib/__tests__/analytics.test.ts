import { describe, it, expect } from 'vitest';
import { calculateKPIs, calculateRevenueByPeriod, calculateCategoryMetrics } from '@/lib/metrics';
import { calculateRFM, aggregateSegments } from '@/lib/rfm';
import { descriptiveStats, histogram, correlationMatrix } from '@/lib/stats';
import { detectDataQuality, cleanData, validateSchema } from '@/lib/validation';
import { formatCurrency, formatNumber, formatPercent, calculateChange } from '@/lib/utils';
import type { Transaction } from '@/lib/types';

function makeTransaction(overrides: Partial<Transaction> = {}): Transaction {
  return {
    transaction_id: 'T001', transaction_date: '2024-06-15', customer_id: 'C001', customer_name: 'Test User',
    customer_age: 35, customer_gender: 'Male', customer_city: 'New York', customer_state: 'New York',
    customer_segment: 'Consumer', product_id: 'P001', product_name: 'Test Product', category: 'Electronics',
    subcategory: 'Phones', brand: 'TestBrand', unit_price: 100, quantity: 2, discount_percent: 10,
    sales_amount: 180, cost_amount: 120, profit_amount: 60, payment_method: 'Credit Card',
    sales_channel: 'Online', store_id: 'S001', store_type: 'Flagship', region: 'East',
    customer_rating: 4, returned: false, ...overrides,
  };
}

describe('KPIs', () => {
  it('calculates correct KPIs from dataset', () => {
    const data = [makeTransaction({ sales_amount: 200, profit_amount: 40 }), makeTransaction({ transaction_id: 'T002', sales_amount: 300, profit_amount: 60 })];
    const kpis = calculateKPIs(data);
    const revenueKpi = kpis.find((k) => k.label === 'Total Revenue');
    expect(revenueKpi?.value).toBe(500);
    const profitKpi = kpis.find((k) => k.label === 'Total Profit');
    expect(profitKpi?.value).toBe(100);
    const marginKpi = kpis.find((k) => k.label === 'Profit Margin');
    expect(marginKpi?.value).toBe(0.2);
  });

  it('calculates change vs previous period', () => {
    const current = [makeTransaction({ sales_amount: 200, profit_amount: 40 })];
    const previous = [makeTransaction({ sales_amount: 100, profit_amount: 20, transaction_id: 'P001' })];
    const kpis = calculateKPIs(current, previous);
    const revenueKpi = kpis.find((k) => k.label === 'Total Revenue');
    expect(revenueKpi?.changePercent).toBeCloseTo(1);
  });
});

describe('Revenue by Period', () => {
  it('groups by month correctly', () => {
    const data = [makeTransaction({ transaction_date: '2024-01-15', sales_amount: 100 }), makeTransaction({ transaction_date: '2024-01-20', sales_amount: 200 }), makeTransaction({ transaction_date: '2024-02-10', sales_amount: 150 })];
    const byMonth = calculateRevenueByPeriod(data, 'month');
    expect(byMonth.length).toBe(2);
    expect(byMonth[0].revenue).toBe(300);
    expect(byMonth[1].revenue).toBe(150);
  });
});

describe('Category Metrics', () => {
  it('groups by category and calculates margin', () => {
    const data = [makeTransaction({ category: 'A', sales_amount: 100, profit_amount: 20 }), makeTransaction({ category: 'B', sales_amount: 200, profit_amount: 60, transaction_id: 'T002' })];
    const cats = calculateCategoryMetrics(data);
    expect(cats.length).toBe(2);
    expect(cats[0].category).toBe('B');
    expect(cats[0].margin).toBeCloseTo(0.3);
  });
});

describe('RFM', () => {
  it('calculates RFM scores', () => {
    const data = Array.from({ length: 10 }, (_, i) => makeTransaction({ customer_id: `C${i}`, transaction_id: `T${i}`, sales_amount: 100 + i * 50, transaction_date: `2024-0${(i % 9) + 1}-15` }));
    const rfm = calculateRFM(data);
    expect(rfm.length).toBeGreaterThan(0);
    rfm.forEach((r) => {
      expect(r.r_score).toBeGreaterThanOrEqual(1);
      expect(r.r_score).toBeLessThanOrEqual(5);
      expect(r.segment).toBeTruthy();
    });
  });

  it('aggregates segments correctly', () => {
    const data = Array.from({ length: 20 }, (_, i) => makeTransaction({ customer_id: `C${i}`, transaction_id: `T${i}`, sales_amount: 100 + i * 100, transaction_date: `2024-0${(i % 9) + 1}-15` }));
    const rfm = calculateRFM(data);
    const segments = aggregateSegments(rfm);
    expect(segments.length).toBeGreaterThan(0);
    const totalCustomers = segments.reduce((a, s) => a + s.customers, 0);
    expect(totalCustomers).toBe(rfm.length);
  });
});

describe('Statistics', () => {
  it('calculates descriptive stats', () => {
    const values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
    const stats = descriptiveStats(values);
    expect(stats.mean).toBe(5.5);
    expect(stats.median).toBe(5.5);
    expect(stats.min).toBe(1);
    expect(stats.max).toBe(10);
    expect(stats.count).toBe(10);
  });

  it('generates histogram bins', () => {
    const values = Array.from({ length: 100 }, (_, i) => i);
    const hist = histogram(values, 10);
    expect(hist.length).toBe(10);
    const total = hist.reduce((a, b) => a + b.count, 0);
    expect(total).toBe(100);
  });

  it('calculates correlation matrix', () => {
    const data = { x: [1, 2, 3, 4, 5], y: [2, 4, 6, 8, 10] };
    const corr = correlationMatrix(data);
    expect(corr.matrix[0][1]).toBeCloseTo(1);
    expect(corr.vars).toEqual(['x', 'y']);
  });
});

describe('Validation', () => {
  it('validates schema correctly', () => {
    const valid = validateSchema(['transaction_id', 'transaction_date', 'customer_id', 'sales_amount', 'product_id', 'category', 'quantity', 'unit_price']);
    expect(valid.valid).toBe(true);
    expect(valid.missing.length).toBe(0);
  });

  it('detects missing columns', () => {
    const result = validateSchema(['transaction_id', 'customer_id']);
    expect(result.valid).toBe(false);
    expect(result.missing.length).toBeGreaterThan(0);
  });

  it('detects data quality issues', () => {
    const data = [makeTransaction({ sales_amount: 100 }), makeTransaction({ transaction_id: 'T001', sales_amount: 200 })];
    const report = detectDataQuality(data);
    expect(report.totalRows).toBe(2);
    expect(report.issues.some((i) => i.type === 'Duplicate Transactions')).toBe(true);
  });

  it('cleans data correctly', () => {
    const data = [makeTransaction({ quantity: -1 }), makeTransaction({ unit_price: 0 }), makeTransaction({ transaction_id: 'DUP' }), makeTransaction({ transaction_id: 'DUP' })];
    const cleaned = cleanData(data);
    expect(cleaned.length).toBeLessThan(data.length);
  });
});

describe('Utils', () => {
  it('formats currency', () => {
    expect(formatCurrency(1234)).toBe('$1,234');
    expect(formatCurrency(1500000, true)).toBe('$1.5M');
  });

  it('formats number', () => {
    expect(formatNumber(1234567)).toBe('1,234,567');
    expect(formatNumber(1500000, true)).toBe('1.5M');
  });

  it('formats percent', () => {
    expect(formatPercent(0.1234)).toBe('12.3%');
  });

  it('calculates change', () => {
    const result = calculateChange(150, 100);
    expect(result.value).toBe(50);
    expect(result.percent).toBe(0.5);
  });
});
