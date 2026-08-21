'use client';
import { useData } from '@/lib/context';
import { KPICard } from '@/components/KPICard';
import { calculateKPIs, calculateRevenueByPeriod, calculateCategoryMetrics, calculateRegionMetrics, calculateProductMetrics } from '@/lib/metrics';
import { formatCurrency } from '@/lib/utils';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line, CartesianGrid } from 'recharts';

export default function OverviewPage() {
  const { filteredData } = useData();
  if (filteredData.length === 0) return <div className="text-center py-20 text-gray-500">Loading data...</div>;

  const kpis = calculateKPIs(filteredData);
  const monthly = calculateRevenueByPeriod(filteredData, 'month');
  const categories = calculateCategoryMetrics(filteredData);
  const regions = calculateRegionMetrics(filteredData);
  const topProducts = calculateProductMetrics(filteredData).slice(0, 10);

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-gray-900">Executive Overview</h2>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {kpis.map((kpi) => <KPICard key={kpi.label} kpi={kpi} />)}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">Revenue Trend</h3>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={monthly}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="period" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => formatCurrency(v, true)} />
              <Tooltip formatter={(v) => formatCurrency(Number(v))} />
              <Line type="monotone" dataKey="revenue" stroke="#2563eb" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">Revenue by Category</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={categories}>
              <XAxis dataKey="category" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => formatCurrency(v, true)} />
              <Tooltip formatter={(v) => formatCurrency(Number(v))} />
              <Bar dataKey="revenue" fill="#2563eb" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">Revenue by Region</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={regions}>
              <XAxis dataKey="region" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => formatCurrency(v, true)} />
              <Tooltip formatter={(v) => formatCurrency(Number(v))} />
              <Bar dataKey="revenue" fill="#10b981" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">Top 10 Products</h3>
          <div className="overflow-y-auto max-h-[280px]">
            <table className="w-full text-sm">
              <thead><tr className="border-b text-left text-gray-500"><th className="py-1 px-2">Product</th><th className="py-1 px-2 text-right">Revenue</th><th className="py-1 px-2 text-right">Margin</th></tr></thead>
              <tbody>
                {topProducts.map((p, i) => (
                  <tr key={i} className="border-b border-gray-50"><td className="py-1.5 px-2 text-gray-800 truncate max-w-[200px]">{p.productName}</td><td className="py-1.5 px-2 text-right">{formatCurrency(p.revenue, true)}</td><td className="py-1.5 px-2 text-right">{(p.margin * 100).toFixed(1)}%</td></tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
