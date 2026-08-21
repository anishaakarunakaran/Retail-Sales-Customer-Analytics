import type { Transaction, RFMSegment, RFMRow } from './types';

export function calculateRFM(data: Transaction[], referenceDate?: Date): RFMRow[] {
  const ref = referenceDate || new Date('2024-12-31');
  const customerMap = new Map<string, { name: string; recency: number; frequency: number; monetary: number }>();

  data.forEach((r) => {
    const daysSince = Math.floor((ref.getTime() - new Date(r.transaction_date).getTime()) / (1000 * 60 * 60 * 24));
    if (!customerMap.has(r.customer_id)) {
      customerMap.set(r.customer_id, { name: r.customer_name, recency: daysSince, frequency: 0, monetary: 0 });
    }
    const c = customerMap.get(r.customer_id)!;
    c.frequency += 1;
    c.monetary += r.sales_amount || 0;
    if (daysSince < c.recency) c.recency = daysSince;
  });

  const customers = Array.from(customerMap.entries()).map(([id, v]) => ({ customer_id: id, customer_name: v.name, recency: v.recency, frequency: v.frequency, monetary: v.monetary }));
  if (customers.length === 0) return [];

  const recencies = customers.map((c) => c.recency).sort((a, b) => b - a);
  const frequencies = customers.map((c) => c.frequency).sort((a, b) => a - b);
  const monetaries = customers.map((c) => c.monetary).sort((a, b) => a - b);

  function quintile(value: number, arr: number[], invert = false): number {
    const sorted = [...arr].sort((a, b) => invert ? b - a : a - b);
    const pct = sorted.indexOf(value) / (sorted.length - 1);
    if (pct <= 0.2) return 1;
    if (pct <= 0.4) return 2;
    if (pct <= 0.6) return 3;
    if (pct <= 0.8) return 4;
    return 5;
  }

  return customers.map((c) => {
    const rScore = quintile(c.recency, recencies, true);
    const fScore = quintile(c.frequency, frequencies);
    const mScore = quintile(c.monetary, monetaries);
    const rfmScore = `${rScore}${fScore}${mScore}`;
    const segment = assignSegment(rScore, fScore, mScore);
    return { ...c, r_score: rScore, f_score: fScore, m_score: mScore, rfm_score: rfmScore, segment };
  });
}

function assignSegment(r: number, f: number, m: number): string {
  if (r >= 4 && f >= 4 && m >= 4) return 'Champions';
  if (r >= 3 && f >= 3 && m >= 3) return 'Loyal Customers';
  if (r >= 4 && f <= 2) return 'New Customers';
  if (r >= 3 && f >= 2 && f <= 4) return 'Potential Loyalists';
  if (r >= 2 && f >= 3) return 'Promising';
  if (r <= 2 && f >= 3 && m >= 3) return 'At Risk';
  if (r <= 2 && f >= 4 && m >= 4) return "Can't Lose";
  if (r <= 2 && f <= 2) return 'Lost';
  return 'Hibernating';
}

export function aggregateSegments(rfmRows: RFMRow[]): RFMSegment[] {
  const segMap = new Map<string, RFMSegment>();
  const colors: Record<string, string> = {
    'Champions': '#10b981', 'Loyal Customers': '#3b82f6', 'Potential Loyalists': '#8b5cf6',
    'New Customers': '#06b6d4', 'Promising': '#f59e0b', 'At Risk': '#ef4444',
    "Can't Lose": '#dc2626', 'Lost': '#6b7280', 'Hibernating': '#9ca3af',
  };

  rfmRows.forEach((r) => {
    if (!segMap.has(r.segment)) {
      segMap.set(r.segment, { segment: r.segment, customers: 0, revenue: 0, avgSpend: 0, avgFrequency: 0, avgRecencyDays: 0, color: colors[r.segment] || '#6b7280' });
    }
    const s = segMap.get(r.segment)!;
    s.customers += 1;
    s.revenue += r.monetary;
    s.avgSpend += r.monetary;
    s.avgFrequency += r.frequency;
    s.avgRecencyDays += r.recency;
  });

  return Array.from(segMap.values()).map((s) => ({
    ...s,
    avgSpend: s.customers > 0 ? s.avgSpend / s.customers : 0,
    avgFrequency: s.customers > 0 ? s.avgFrequency / s.customers : 0,
    avgRecencyDays: s.customers > 0 ? s.avgRecencyDays / s.customers : 0,
  })).sort((a, b) => b.revenue - a.revenue);
}
