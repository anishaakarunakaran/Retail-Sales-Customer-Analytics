'use client';
import { useData } from '@/lib/context';
import { calculateRevenueByPeriod, calculateCategoryMetrics, calculateRegionMetrics, calculateChannelMetrics, calculatePaymentMetrics } from '@/lib/metrics';
import { formatCurrency } from '@/lib/utils';
import { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line, CartesianGrid, PieChart, Pie, Cell } from 'recharts';

const COLORS = ['#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

export default function SalesPage() {
  const { filteredData } = useData();
  const [granularity, setGranularity] = useState<'month' | 'quarter' | 'year'>('month');
  if (filteredData.length === 0) return <div className="text-center py-20 text-gray-500">Loading...</div>;

  const byPeriod = calculateRevenueByPeriod(filteredData, granularity);
  const categories = calculateCategoryMetrics(filteredData);
  const regions = calculateRegionMetrics(filteredData);
  const channels = calculateChannelMetrics(filteredData);
  const payments = calculatePaymentMetrics(filteredData);

  const totalRev = filteredData.reduce((a, r) => a + r.sales_amount, 0);
  const totalProfit = filteredData.reduce((a, r) => a + r.profit_amount, 0);
  const totalCost = totalRev - totalProfit;

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-gray-900">Sales Analytics</h2>

      <div className="flex gap-2">
        {(['month', 'quarter', 'year'] as const).map((g) => (
          <button key={g} onClick={() => setGranularity(g)} className={`px-3 py-1.5 text-sm rounded-md border ${granularity === g ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-gray-600 border-gray-300 hover:bg-gray-50'}`}>
            {g.charAt(0).toUpperCase() + g.slice(1)}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">Revenue & Profit by {granularity}</h3>
          <ResponsiveContainer width="100%" height={320}>
            <LineChart data={byPeriod}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="period" tick={{ fontSize: 10 }} />
              <YAxis tick={{ fontSize: 10 }} tickFormatter={(v) => formatCurrency(v, true)} />
              <Tooltip formatter={(v) => formatCurrency(Number(v))} />
              <Line type="monotone" dataKey="revenue" stroke="#2563eb" strokeWidth={2} dot={false} name="Revenue" />
              <Line type="monotone" dataKey="profit" stroke="#10b981" strokeWidth={2} dot={false} name="Profit" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">Revenue by Category</h3>
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={categories}>
              <XAxis dataKey="category" tick={{ fontSize: 10 }} />
              <YAxis tick={{ fontSize: 10 }} tickFormatter={(v) => formatCurrency(v, true)} />
              <Tooltip formatter={(v) => formatCurrency(Number(v))} />
              <Bar dataKey="revenue" fill="#2563eb" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">Revenue by Region</h3>
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={regions}>
              <XAxis dataKey="region" tick={{ fontSize: 10 }} />
              <YAxis tick={{ fontSize: 10 }} tickFormatter={(v) => formatCurrency(v, true)} />
              <Tooltip formatter={(v) => formatCurrency(Number(v))} />
              <Bar dataKey="revenue" fill="#10b981" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">Revenue vs Cost vs Profit</h3>
          <div className="space-y-3 mt-4">
            {[{ label: 'Revenue', value: totalRev, color: 'bg-blue-600' }, { label: 'Cost', value: totalCost, color: 'bg-amber-500' }, { label: 'Profit', value: totalProfit, color: 'bg-emerald-600' }].map((item) => (
              <div key={item.label}>
                <div className="flex justify-between text-sm mb-1"><span className="text-gray-600">{item.label}</span><span className="font-medium">{formatCurrency(item.value)}</span></div>
                <div className="w-full bg-gray-100 rounded-full h-2"><div className={`${item.color} h-2 rounded-full`} style={{ width: `${(item.value / totalRev) * 100}%` }} /></div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">Sales Channel</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie data={channels} dataKey="revenue" nameKey="channel" cx="50%" cy="50%" outerRadius={80} label={({ channel, percent }: { channel?: string; percent?: number }) => `${channel}: ${((percent || 0) * 100).toFixed(0)}%`}>
                {channels.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Pie>
              <Tooltip formatter={(v) => formatCurrency(Number(v))} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">Payment Methods</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={payments} layout="vertical">
              <XAxis type="number" tick={{ fontSize: 10 }} tickFormatter={(v) => formatCurrency(v, true)} />
              <YAxis type="category" dataKey="method" tick={{ fontSize: 10 }} width={100} />
              <Tooltip formatter={(v) => formatCurrency(Number(v))} />
              <Bar dataKey="revenue" fill="#8b5cf6" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
