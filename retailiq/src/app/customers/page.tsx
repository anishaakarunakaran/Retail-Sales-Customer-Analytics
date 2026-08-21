'use client';
import { useData } from '@/lib/context';
import { calculateKPIs, calculateTopCustomers, calculateRegionMetrics } from '@/lib/metrics';
import { KPICard } from '@/components/KPICard';
import { formatCurrency } from '@/lib/utils';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const COLORS = ['#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

export default function CustomersPage() {
  const { filteredData } = useData();
  if (filteredData.length === 0) return <div className="text-center py-20 text-gray-500">Loading...</div>;

  const kpis = calculateKPIs(filteredData);
  const topCustomers = calculateTopCustomers(filteredData).slice(0, 15);
  const regions = calculateRegionMetrics(filteredData);

  const totalCustomers = new Set(filteredData.map((r) => r.customer_id)).size;
  const repeatCustomers = filteredData.reduce((acc, r) => { acc[r.customer_id] = (acc[r.customer_id] || 0) + 1; return acc; }, {} as Record<string, number>);
  const repeatCount = Object.values(repeatCustomers).filter((c) => c > 1).length;

  const segmentData = Object.entries(filteredData.reduce((acc, r) => {
    if (!acc[r.customer_segment]) acc[r.customer_segment] = { revenue: 0, count: new Set<string>() };
    acc[r.customer_segment].revenue += r.sales_amount;
    acc[r.customer_segment].count.add(r.customer_id);
    return acc;
  }, {} as Record<string, { revenue: number; count: Set<string> }>)).map(([segment, v]) => ({ segment, revenue: v.revenue, customers: v.count.size })).sort((a, b) => b.revenue - a.revenue);

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-gray-900">Customer Analytics</h2>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <KPICard kpi={{ label: 'Total Customers', value: totalCustomers, previousValue: null, change: null, changePercent: null, format: 'number' }} />
        <KPICard kpi={{ label: 'Repeat Customers', value: repeatCount, previousValue: null, change: null, changePercent: null, format: 'number' }} />
        <KPICard kpi={{ label: 'Repeat Rate', value: totalCustomers > 0 ? repeatCount / totalCustomers : 0, previousValue: null, change: null, changePercent: null, format: 'percent' }} />
        {kpis.filter((k) => k.label === 'Average Order Value').map((kpi) => <KPICard key={kpi.label} kpi={kpi} />)}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">Revenue by Segment</h3>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie data={segmentData} dataKey="revenue" nameKey="segment" cx="50%" cy="50%" outerRadius={90} label={({ segment, percent }: { segment?: string; percent?: number }) => `${segment}: ${((percent || 0) * 100).toFixed(0)}%`}>
                {segmentData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Pie>
              <Tooltip formatter={(v) => formatCurrency(Number(v))} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">Customers by Region</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={regions}>
              <XAxis dataKey="region" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="customers" fill="#8b5cf6" radius={[4, 4, 0, 0]} name="Customers" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-4 lg:col-span-2">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">Top 15 Customers</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead><tr className="border-b text-left text-gray-500"><th className="py-2 px-2">Customer</th><th className="py-2 px-2">Segment</th><th className="py-2 px-2">Region</th><th className="py-2 px-2 text-right">Revenue</th><th className="py-2 px-2 text-right">Orders</th><th className="py-2 px-2 text-right">Avg Rating</th></tr></thead>
              <tbody>{topCustomers.map((c, i) => <tr key={i} className="border-b hover:bg-gray-50"><td className="py-2 px-2 font-medium">{c.name}</td><td className="py-2 px-2">{c.segment}</td><td className="py-2 px-2">{c.region}</td><td className="py-2 px-2 text-right">{formatCurrency(c.revenue)}</td><td className="py-2 px-2 text-right">{c.orders}</td><td className="py-2 px-2 text-right">{c.avgRating.toFixed(1)}</td></tr>)}</tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
