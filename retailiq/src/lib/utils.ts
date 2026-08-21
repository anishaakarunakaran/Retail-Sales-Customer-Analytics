import Papa from 'papaparse';
import * as XLSX from 'xlsx';
import type { Transaction } from './types';

export function formatCurrency(value: number, compact = false): string {
  if (compact && Math.abs(value) >= 1e6) return `$${(value / 1e6).toFixed(1)}M`;
  if (compact && Math.abs(value) >= 1e3) return `$${(value / 1e3).toFixed(1)}K`;
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(value);
}

export function formatNumber(value: number, compact = false): string {
  if (compact && Math.abs(value) >= 1e6) return `${(value / 1e6).toFixed(1)}M`;
  if (compact && Math.abs(value) >= 1e3) return `${(value / 1e3).toFixed(1)}K`;
  return new Intl.NumberFormat('en-US').format(value);
}

export function formatPercent(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

export function formatChange(value: number): { text: string; positive: boolean } {
  const sign = value >= 0 ? '+' : '';
  return { text: `${sign}${(value * 100).toFixed(1)}%`, positive: value >= 0 };
}

export function calculateChange(current: number, previous: number): { value: number; percent: number } {
  if (previous === 0) return { value: current, percent: 0 };
  return { value: current - previous, percent: (current - previous) / Math.abs(previous) };
}

export function parseCSV(text: string): Transaction[] {
  const result = Papa.parse(text, { header: true, skipEmptyLines: true, dynamicTyping: true });
  return result.data as Transaction[];
}

export function parseExcel(buffer: ArrayBuffer): Transaction[] {
  const workbook = XLSX.read(buffer, { type: 'array' });
  const sheetName = workbook.SheetNames[0];
  const sheet = workbook.Sheets[sheetName];
  return XLSX.utils.sheet_to_json<Transaction>(sheet);
}

export function classNames(...classes: (string | boolean | undefined | null | 0)[]): string {
  return classes.filter(Boolean).join(' ');
}

export function debounce<T extends (...args: unknown[]) => unknown>(fn: T, ms: number): T {
  let timer: ReturnType<typeof setTimeout>;
  return ((...args: unknown[]) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), ms);
  }) as T;
}

export function generateId(): string {
  return Math.random().toString(36).substring(2, 10) + Date.now().toString(36);
}
