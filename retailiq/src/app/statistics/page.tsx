'use client';
import { useData } from '@/lib/context';
import { descriptiveStats, histogram, correlationMatrix } from '@/lib/stats';
import { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

const NUM_FIELDS = ['sales_amount', 'profit_amount', 'quantity', 'unit_price', 'discount_percent', 'customer_age', 'customer_rating'] as const;

export default function StatisticsPage() {
  const { filteredData } = useData();
  const [selectedField, setSelectedField] = useState<string>('sales_amount');
  if (filteredData.length === 0) return <div className="text-center py-20 text-gray-500">Loading...</div>;

  const values = filteredData.map((r) => Number(r[selectedField as keyof typeof r])).filter((v) => !isNaN(v) && isFinite(v));
  const stats = descriptiveStats(values);
  const hist = histogram(values, 25);

  const corrData: Record<string, number[]> = {};
  NUM_FIELDS.forEach((f) => { corrData[f] = filteredData.map((r) => Number(r[f])).filter((v) => !isNaN(v)); });
  const corr = correlationMatrix(corrData);

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-gray-900">Statistical Analysis</h2>

      <div className="flex flex-wrap gap-2">
        {NUM_FIELDS.map((f) => (
          <button key={f} onClick={() => setSelectedField(f)} className={`px-3 py-1.5 text-sm rounded-md border ${selectedField === f ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-gray-600 border-gray-300'}`}>
            {f.replace(/_/g, ' ')}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">Distribution: {selectedField.replace(/_/g, ' ')}</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={hist}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="range" tick={{ fontSize: 8 }} angle={-45} textAnchor="end" />
              <YAxis tick={{ fontSize: 10 }} />
              <Tooltip />
              <Bar dataKey="count" fill="#2563eb" radius={[2, 2, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">Descriptive Statistics</h3>
          <table className="w-full text-sm">
            <tbody>
              {Object.entries(stats).map(([key, val]) => (
                <tr key={key} className="border-b"><td className="py-2 px-2 text-gray-500 font-medium">{key}</td><td className="py-2 px-2 text-right font-mono">{typeof val === 'number' ? val.toLocaleString(undefined, { maximumFractionDigits: 4 }) : val}</td></tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-4 lg:col-span-2">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">Correlation Matrix</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead><tr><th className="p-2"></th>{corr.vars.map((v) => <th key={v} className="p-2 text-center font-medium text-gray-600">{v}</th>)}</tr></thead>
              <tbody>{corr.matrix.map((row, i) => <tr key={i}><td className="p-2 font-medium text-gray-600">{corr.vars[i]}</td>{row.map((val, j) => <td key={j} className="p-2 text-center" style={{ backgroundColor: i === j ? '#dbeafe' : `rgba(37,99,235,${Math.abs(val) * 0.3})`, color: Math.abs(val) > 0.5 ? '#fff' : '#374151' }}>{val.toFixed(2)}</td>)}</tr>)}</tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
