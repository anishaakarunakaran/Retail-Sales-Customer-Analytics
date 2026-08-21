'use client';
import { formatCurrency, formatNumber, formatPercent } from '@/lib/utils';

interface TableProps {
  data: Record<string, unknown>[];
  columns: { key: string; label: string; format?: 'currency' | 'number' | 'percent' | 'text' }[];
  pageSize?: number;
}

export function DataTable({ data, columns, pageSize = 15 }: TableProps) {
  const fmt = (v: unknown, f?: string) => {
    if (v === null || v === undefined) return '-';
    if (f === 'currency') return formatCurrency(Number(v), true);
    if (f === 'number') return formatNumber(Number(v), true);
    if (f === 'percent') return formatPercent(Number(v));
    return String(v);
  };

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-sm">
        <thead>
          <tr className="border-b border-gray-200">
            {columns.map((c) => (
              <th key={c.key} className="text-left px-3 py-2 font-medium text-gray-600 bg-gray-50">{c.label}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.slice(0, pageSize).map((row, i) => (
            <tr key={i} className="border-b border-gray-100 hover:bg-gray-50">
              {columns.map((c) => (
                <td key={c.key} className="px-3 py-2 text-gray-800">{fmt(row[c.key], c.format)}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      <div className="text-xs text-gray-500 mt-2 px-3">
        Showing {Math.min(pageSize, data.length)} of {data.length} rows
      </div>
    </div>
  );
}
