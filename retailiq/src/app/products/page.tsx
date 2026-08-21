'use client';
import { useData } from '@/lib/context';
import { calculateProductMetrics, calculateCategoryMetrics } from '@/lib/metrics';
import { formatCurrency } from '@/lib/utils';
import { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, ScatterChart, Scatter, CartesianGrid } from 'recharts';

export default function ProductsPage() {
  const { filteredData } = useData();
  const [topN, setTopN] = useState(10);
  if (filteredData.length === 0) return <div className="text-center py-20 text-gray-500">Loading...</div>;

  const products = calculateProductMetrics(filteredData);
  const categories = calculateCategoryMetrics(filteredData);
  const topProducts = products.slice(0, topN);
  const bottomProducts = products.slice(-10).reverse();

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-gray-900">Product Analytics</h2>

      <div className="flex gap-2">
        {[10, 20, 50].map((n) => (
          <button key={n} onClick={() => setTopN(n)} className={`px-3 py-1.5 text-sm rounded-md border ${topN === n ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-gray-600 border-gray-300'}`}>
            Top {n}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">Top Products by Revenue</h3>
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={topProducts} layout="vertical">
              <XAxis type="number" tick={{ fontSize: 10 }} tickFormatter={(v) => formatCurrency(v, true)} />
              <YAxis type="category" dataKey="productName" tick={{ fontSize: 9 }} width={150} />
              <Tooltip formatter={(v) => formatCurrency(Number(v))} />
              <Bar dataKey="revenue" fill="#2563eb" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">Profitability Matrix</h3>
          <ResponsiveContainer width="100%" height={350}>
            <ScatterChart>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis type="number" dataKey="revenue" name="Revenue" tick={{ fontSize: 10 }} tickFormatter={(v) => formatCurrency(v, true)} />
              <YAxis type="number" dataKey="margin" name="Margin" tick={{ fontSize: 10 }} tickFormatter={(v) => `${(v * 100).toFixed(0)}%`} />
              <Tooltip formatter={(v, name) => name === 'Margin' ? `${(Number(v) * 100).toFixed(1)}%` : formatCurrency(Number(v))} />
              <Scatter data={products.slice(0, 50)} fill="#2563eb" />
            </ScatterChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">Category Performance</h3>
          <table className="w-full text-sm">
            <thead><tr className="border-b text-left text-gray-500"><th className="py-2 px-2">Category</th><th className="py-2 px-2 text-right">Revenue</th><th className="py-2 px-2 text-right">Profit</th><th className="py-2 px-2 text-right">Margin</th><th className="py-2 px-2 text-right">Orders</th></tr></thead>
            <tbody>{categories.map((c, i) => <tr key={i} className="border-b"><td className="py-2 px-2 font-medium">{c.category}</td><td className="py-2 px-2 text-right">{formatCurrency(c.revenue, true)}</td><td className="py-2 px-2 text-right">{formatCurrency(c.profit, true)}</td><td className="py-2 px-2 text-right">{(c.margin * 100).toFixed(1)}%</td><td className="py-2 px-2 text-right">{c.orders.toLocaleString()}</td></tr>)}</tbody>
          </table>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">Bottom 10 Products</h3>
          <table className="w-full text-sm">
            <thead><tr className="border-b text-left text-gray-500"><th className="py-2 px-2">Product</th><th className="py-2 px-2 text-right">Revenue</th><th className="py-2 px-2 text-right">Margin</th></tr></thead>
            <tbody>{bottomProducts.map((p, i) => <tr key={i} className="border-b"><td className="py-2 px-2 truncate max-w-[200px]">{p.productName}</td><td className="py-2 px-2 text-right">{formatCurrency(p.revenue, true)}</td><td className="py-2 px-2 text-right">{(p.margin * 100).toFixed(1)}%</td></tr>)}</tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
