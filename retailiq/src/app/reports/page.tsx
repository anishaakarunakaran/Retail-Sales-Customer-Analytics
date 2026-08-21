'use client';
import { useData } from '@/lib/context';
import { calculateKPIs, calculateCategoryMetrics, calculateRegionMetrics } from '@/lib/metrics';
import { generateInsights } from '@/lib/insights';
import { formatCurrency, formatPercent } from '@/lib/utils';
import { exportCSV, exportExcel } from '@/lib/exports';
import { useState } from 'react';

export default function ReportsPage() {
  const { filteredData, filters, datasetName } = useData();
  const [reportType, setReportType] = useState<string>('executive');
  if (filteredData.length === 0) return <div className="text-center py-20 text-gray-500">Loading...</div>;

  const kpis = calculateKPIs(filteredData);
  const cats = calculateCategoryMetrics(filteredData);
  const regions = calculateRegionMetrics(filteredData);
  const insights = generateInsights(filteredData);

  const titles: Record<string, string> = {
    executive: 'Executive Sales Report',
    customer: 'Customer Analytics Report',
    product: 'Product Performance Report',
    regional: 'Regional Performance Report',
  };

  const generateReportData = () => {
    return {
      title: titles[reportType] || 'Report',
      date: new Date().toISOString().split('T')[0],
      dataset: datasetName,
      filters: JSON.stringify(filters),
      kpis: kpis.map((k) => ({ label: k.label, value: k.format === 'currency' ? formatCurrency(k.value) : k.format === 'percent' ? formatPercent(k.value) : String(k.value) })),
      categories: cats.map((c) => ({ category: c.category, revenue: formatCurrency(c.revenue), margin: formatPercent(c.margin), orders: c.orders })),
      regions: regions.map((r) => ({ region: r.region, revenue: formatCurrency(r.revenue), customers: r.customers })),
      insights: insights.map((i) => ({ title: i.title, description: i.description, impact: i.impact })),
    };
  };

  const exportReportCSV = () => {
    const report = generateReportData();
    exportCSV([{ ...report }], `${reportType}_report.csv`);
  };

  const exportReportExcel = () => {
    const report = generateReportData();
    exportExcel([{ ...report }], `${reportType}_report.xlsx`);
  };

  const activeFilters = Object.entries(filters).filter(([, v]) => Array.isArray(v) ? v.length > 0 : v !== null);

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-gray-900">Reports</h2>

      <div className="flex flex-wrap gap-2">
        {Object.keys(titles).map((type) => (
          <button key={type} onClick={() => setReportType(type)} className={`px-3 py-1.5 text-sm rounded-md border ${reportType === type ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-gray-600 border-gray-300'}`}>
            {titles[type]}
          </button>
        ))}
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <div className="border-b pb-4 mb-4">
          <h1 className="text-2xl font-bold text-gray-900">{titles[reportType]}</h1>
          <p className="text-sm text-gray-500 mt-1">Generated: {new Date().toLocaleDateString()} | Dataset: {datasetName}</p>
          {activeFilters.length > 0 && (
            <p className="text-xs text-gray-400 mt-1">Active filters: {activeFilters.map(([k]) => k).join(', ')}</p>
          )}
        </div>

        <section className="mb-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-3">Key Metrics</h2>
          <div className="grid grid-cols-4 gap-3">
            {kpis.slice(0, 8).map((k) => (
              <div key={k.label} className="text-center p-3 bg-gray-50 rounded">
                <div className="text-xs text-gray-500">{k.label}</div>
                <div className="text-lg font-bold text-gray-900">{k.format === 'currency' ? formatCurrency(k.value) : k.format === 'percent' ? formatPercent(k.value) : k.value.toLocaleString()}</div>
              </div>
            ))}
          </div>
        </section>

        <section className="mb-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-3">Category Performance</h2>
          <table className="w-full text-sm border">
            <thead><tr className="bg-gray-50 border-b"><th className="py-2 px-3 text-left">Category</th><th className="py-2 px-3 text-right">Revenue</th><th className="py-2 px-3 text-right">Margin</th><th className="py-2 px-3 text-right">Orders</th></tr></thead>
            <tbody>{cats.map((c, i) => <tr key={i} className="border-b"><td className="py-2 px-3">{c.category}</td><td className="py-2 px-3 text-right">{formatCurrency(c.revenue)}</td><td className="py-2 px-3 text-right">{formatPercent(c.margin)}</td><td className="py-2 px-3 text-right">{c.orders}</td></tr>)}</tbody>
          </table>
        </section>

        <section className="mb-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-3">Key Findings</h2>
          <div className="space-y-2">{insights.slice(0, 6).map((ins) => <div key={ins.id} className="p-3 bg-gray-50 rounded"><div className="text-sm font-medium">{ins.title}</div><div className="text-xs text-gray-500 mt-1">{ins.description}</div></div>)}</div>
        </section>

        <div className="flex gap-3 pt-4 border-t">
          <button onClick={exportReportCSV} className="px-4 py-2 text-sm bg-blue-600 text-white rounded-md">Export CSV</button>
          <button onClick={exportReportExcel} className="px-4 py-2 text-sm bg-emerald-600 text-white rounded-md">Export Excel</button>
          <button onClick={() => window.print()} className="px-4 py-2 text-sm bg-gray-600 text-white rounded-md">Print / PDF</button>
        </div>
      </div>
    </div>
  );
}
