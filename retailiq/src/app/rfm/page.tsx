'use client';
import { useData } from '@/lib/context';
import { calculateRFM, aggregateSegments } from '@/lib/rfm';
import { formatCurrency } from '@/lib/utils';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { useState } from 'react';

export default function RFMPage() {
  const { filteredData } = useData();
  const [selectedSegment, setSelectedSegment] = useState<string | null>(null);
  if (filteredData.length === 0) return <div className="text-center py-20 text-gray-500">Loading...</div>;

  const rfm = calculateRFM(filteredData);
  const segments = aggregateSegments(rfm);
  const filtered = selectedSegment ? rfm.filter((r) => r.segment === selectedSegment) : rfm;

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-gray-900">RFM Customer Segmentation</h2>
      <p className="text-sm text-gray-500">Recency, Frequency, Monetary analysis on {rfm.length} customers.</p>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {segments.map((s) => (
          <button key={s.segment} onClick={() => setSelectedSegment(selectedSegment === s.segment ? null : s.segment)} className={`p-3 rounded-lg border text-left transition-all ${selectedSegment === s.segment ? 'border-blue-500 bg-blue-50 ring-1 ring-blue-200' : 'border-gray-200 bg-white hover:border-gray-300'}`}>
            <div className="text-xs font-medium text-gray-500">{s.segment}</div>
            <div className="text-lg font-bold" style={{ color: s.color }}>{s.customers}</div>
            <div className="text-xs text-gray-400">{formatCurrency(s.revenue, true)} revenue</div>
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">Segment Revenue</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={segments}>
              <XAxis dataKey="segment" tick={{ fontSize: 9 }} angle={-30} textAnchor="end" />
              <YAxis tick={{ fontSize: 10 }} tickFormatter={(v) => formatCurrency(v, true)} />
              <Tooltip formatter={(v) => formatCurrency(Number(v))} />
              <Bar dataKey="revenue" radius={[4, 4, 0, 0]}>
                {segments.map((s, i) => <Cell key={i} fill={s.color} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">Segment Summary</h3>
          <table className="w-full text-sm">
            <thead><tr className="border-b text-left text-gray-500"><th className="py-2 px-2">Segment</th><th className="py-2 px-2 text-right">Customers</th><th className="py-2 px-2 text-right">Avg Spend</th><th className="py-2 px-2 text-right">Avg Freq</th><th className="py-2 px-2 text-right">Avg Recency</th></tr></thead>
            <tbody>{segments.map((s, i) => <tr key={i} className="border-b hover:bg-gray-50"><td className="py-2 px-2 font-medium" style={{ color: s.color }}>{s.segment}</td><td className="py-2 px-2 text-right">{s.customers}</td><td className="py-2 px-2 text-right">{formatCurrency(s.avgSpend)}</td><td className="py-2 px-2 text-right">{s.avgFrequency.toFixed(1)}</td><td className="py-2 px-2 text-right">{s.avgRecencyDays.toFixed(0)}d</td></tr>)}</tbody>
          </table>
        </div>
      </div>

      {selectedSegment && (
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">Customers in: {selectedSegment}</h3>
          <div className="overflow-x-auto max-h-80 overflow-y-auto">
            <table className="w-full text-sm">
              <thead><tr className="border-b text-left text-gray-500 sticky top-0 bg-white"><th className="py-2 px-2">Customer</th><th className="py-2 px-2 text-right">Recency</th><th className="py-2 px-2 text-right">Frequency</th><th className="py-2 px-2 text-right">Monetary</th><th className="py-2 px-2">RFM Score</th></tr></thead>
              <tbody>{filtered.map((r, i) => <tr key={i} className="border-b"><td className="py-1.5 px-2">{r.customer_id}</td><td className="py-1.5 px-2 text-right">{r.recency}d</td><td className="py-1.5 px-2 text-right">{r.frequency}</td><td className="py-1.5 px-2 text-right">{formatCurrency(r.monetary)}</td><td className="py-1.5 px-2">{r.rfm_score}</td></tr>)}</tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
