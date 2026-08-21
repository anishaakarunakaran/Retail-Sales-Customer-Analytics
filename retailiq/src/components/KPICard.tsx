'use client';
import type { KPI } from '@/lib/types';
import { formatCurrency, formatNumber, formatPercent } from '@/lib/utils';

export function KPICard({ kpi }: { kpi: KPI }) {
  const formatValue = (v: number, fmt: KPI['format']) => {
    switch (fmt) {
      case 'currency': return formatCurrency(v, true);
      case 'number': return formatNumber(v, true);
      case 'percent': return formatPercent(v);
      case 'decimal': return v.toFixed(2);
      default: return String(v);
    }
  };

  const trendColor = kpi.trend === 'up' ? 'text-emerald-600' : kpi.trend === 'down' ? 'text-red-600' : 'text-gray-500';
  const trendIcon = kpi.trend === 'up' ? '\u2191' : kpi.trend === 'down' ? '\u2193' : '\u2192';

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4">
      <div className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">{kpi.label}</div>
      <div className="text-2xl font-bold text-gray-900 mb-1">{formatValue(kpi.value, kpi.format)}</div>
      {kpi.changePercent !== null && (
        <div className={`text-xs font-medium ${trendColor}`}>
          {trendIcon} {kpi.changePercent >= 0 ? '+' : ''}{(kpi.changePercent * 100).toFixed(1)}% vs prior period
        </div>
      )}
      {kpi.previousValue !== null && (
        <div className="text-xs text-gray-400 mt-0.5">
          Prev: {formatValue(kpi.previousValue, kpi.format)}
        </div>
      )}
    </div>
  );
}
