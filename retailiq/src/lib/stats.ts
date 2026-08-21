import type { StatisticalSummary } from './types';

export function descriptiveStats(values: number[]): StatisticalSummary {
  const clean = values.filter((v) => !isNaN(v) && isFinite(v));
  if (clean.length === 0) return { mean: 0, median: 0, mode: 0, min: 0, max: 0, std: 0, variance: 0, q1: 0, q3: 0, iqr: 0, count: 0 };

  const sorted = [...clean].sort((a, b) => a - b);
  const n = sorted.length;
  const mean = clean.reduce((a, b) => a + b, 0) / n;
  const median = n % 2 === 0 ? (sorted[n / 2 - 1] + sorted[n / 2]) / 2 : sorted[Math.floor(n / 2)];
  const variance = clean.reduce((acc, v) => acc + (v - mean) ** 2, 0) / n;
  const std = Math.sqrt(variance);
  const q1 = sorted[Math.floor(n * 0.25)];
  const q3 = sorted[Math.floor(n * 0.75)];
  const iqr = q3 - q1;

  const freq = new Map<number, number>();
  clean.forEach((v) => freq.set(v, (freq.get(v) || 0) + 1));
  let mode = sorted[0];
  let maxFreq = 0;
  freq.forEach((f, v) => { if (f > maxFreq) { maxFreq = f; mode = v; } });

  return { mean, median, mode, min: sorted[0], max: sorted[n - 1], std, variance, q1, q3, iqr, count: n };
}

export function histogram(values: number[], bins = 20): { range: string; count: number }[] {
  const clean = values.filter((v) => !isNaN(v) && isFinite(v));
  if (clean.length === 0) return [];
  const min = Math.min(...clean);
  const max = Math.max(...clean);
  const binWidth = (max - min) / bins;
  const result: { range: string; count: number }[] = [];

  for (let i = 0; i < bins; i++) {
    const lo = min + i * binWidth;
    const hi = min + (i + 1) * binWidth;
    const count = clean.filter((v) => i === bins - 1 ? v >= lo && v <= hi : v >= lo && v < hi).length;
    result.push({ range: `${lo.toFixed(1)}-${hi.toFixed(1)}`, count });
  }
  return result;
}

export function correlationMatrix(data: Record<string, number[]>): { vars: string[]; matrix: number[][] } {
  const vars = Object.keys(data);
  const n = vars.length;
  const matrix: number[][] = Array.from({ length: n }, () => Array(n).fill(0));

  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n; j++) {
      if (i === j) { matrix[i][j] = 1; continue; }
      const a = data[vars[i]];
      const b = data[vars[j]];
      const len = Math.min(a.length, b.length);
      if (len < 2) { matrix[i][j] = 0; continue; }
      const meanA = a.slice(0, len).reduce((x, y) => x + y, 0) / len;
      const meanB = b.slice(0, len).reduce((x, y) => x + y, 0) / len;
      let num = 0, denA = 0, denB = 0;
      for (let k = 0; k < len; k++) {
        const da = a[k] - meanA;
        const db = b[k] - meanB;
        num += da * db;
        denA += da * da;
        denB += db * db;
      }
      matrix[i][j] = denA && denB ? num / Math.sqrt(denA * denB) : 0;
    }
  }
  return { vars, matrix };
}

export function boxPlotStats(values: number[]): { min: number; q1: number; median: number; q3: number; max: number; outliers: number[] } {
  const clean = values.filter((v) => !isNaN(v) && isFinite(v)).sort((a, b) => a - b);
  if (clean.length === 0) return { min: 0, q1: 0, median: 0, q3: 0, max: 0, outliers: [] };
  const n = clean.length;
  const q1 = clean[Math.floor(n * 0.25)];
  const q3 = clean[Math.floor(n * 0.75)];
  const iqr = q3 - q1;
  const lowerFence = q1 - 1.5 * iqr;
  const upperFence = q3 + 1.5 * iqr;
  const outliers = clean.filter((v) => v < lowerFence || v > upperFence);
  return { min: Math.max(clean[0], lowerFence), q1, median: clean[Math.floor(n / 2)], q3, max: Math.min(clean[n - 1], upperFence), outliers };
}
