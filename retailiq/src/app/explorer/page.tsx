'use client';
import { useData } from '@/lib/context';
import { useState, useMemo } from 'react';
import { formatCurrency } from '@/lib/utils';
import { exportCSV } from '@/lib/exports';

export default function ExplorerPage() {
  const { filteredData } = useData();
  const [search, setSearch] = useState('');
  const [sortKey, setSortKey] = useState('sales_amount');
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('desc');
  const [page, setPage] = useState(0);
  const [visibleCols, setVisibleCols] = useState(['transaction_id', 'transaction_date', 'customer_name', 'product_name', 'category', 'sales_amount', 'quantity', 'profit_amount', 'region']);
  const pageSize = 25;

  const allCols = ['transaction_id', 'transaction_date', 'customer_id', 'customer_name', 'product_name', 'category', 'subcategory', 'brand', 'sales_amount', 'quantity', 'unit_price', 'discount_percent', 'profit_amount', 'region', 'customer_state', 'customer_segment', 'payment_method', 'sales_channel'];

  const processed = useMemo(() => {
    let data = [...filteredData];
    if (search) {
      const q = search.toLowerCase();
      data = data.filter((r) => Object.values(r).some((v) => String(v).toLowerCase().includes(q)));
    }
    data.sort((a, b) => {
      const av = Number(a[sortKey as keyof typeof a]) || 0;
      const bv = Number(b[sortKey as keyof typeof b]) || 0;
      return sortDir === 'asc' ? av - bv : bv - av;
    });
    return data;
  }, [filteredData, search, sortKey, sortDir]);

  const paged = processed.slice(page * pageSize, (page + 1) * pageSize);
  const totalPages = Math.ceil(processed.length / pageSize);

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold text-gray-900">Data Explorer</h2>

      <div className="flex flex-wrap items-center gap-3">
        <input type="text" placeholder="Search..." value={search} onChange={(e) => { setSearch(e.target.value); setPage(0); }} className="px-3 py-1.5 text-sm border border-gray-300 rounded-md w-64" />
        <select value={sortKey} onChange={(e) => setSortKey(e.target.value)} className="px-3 py-1.5 text-sm border border-gray-300 rounded-md">
          {allCols.map((c) => <option key={c} value={c}>{c.replace(/_/g, ' ')}</option>)}
        </select>
        <button onClick={() => setSortDir(sortDir === 'asc' ? 'desc' : 'asc')} className="px-2 py-1.5 text-sm border border-gray-300 rounded-md">{sortDir === 'asc' ? 'ASC' : 'DESC'}</button>
        <button onClick={() => exportCSV(processed.map((r) => Object.fromEntries(visibleCols.map((c) => [c, r[c as keyof typeof r]]))), 'export.csv')} className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded-md">Export CSV</button>
        <span className="text-sm text-gray-500 ml-auto">{processed.length} rows</span>
      </div>

      <div className="flex flex-wrap gap-1 mb-2">
        {allCols.map((c) => (
          <button key={c} onClick={() => setVisibleCols(visibleCols.includes(c) ? visibleCols.filter((x) => x !== c) : [...visibleCols, c])} className={`text-xs px-2 py-1 rounded border ${visibleCols.includes(c) ? 'bg-blue-100 border-blue-300 text-blue-700' : 'bg-white border-gray-200 text-gray-500'}`}>
            {c.replace(/_/g, ' ')}
          </button>
        ))}
      </div>

      <div className="overflow-x-auto bg-white border border-gray-200 rounded-lg">
        <table className="w-full text-sm">
          <thead><tr className="border-b bg-gray-50">{visibleCols.map((c) => <th key={c} onClick={() => { setSortKey(c); setSortDir(sortDir === 'asc' && sortKey === c ? 'desc' : 'asc'); }} className="py-2 px-2 text-left font-medium text-gray-600 cursor-pointer hover:text-gray-900">{c.replace(/_/g, ' ')}</th>)}</tr></thead>
          <tbody>{paged.map((row, i) => <tr key={i} className="border-b hover:bg-gray-50">{visibleCols.map((c) => <td key={c} className="py-1.5 px-2 text-gray-800 truncate max-w-[200px]">{c === 'sales_amount' || c === 'profit_amount' || c === 'unit_price' ? formatCurrency(Number(row[c as keyof typeof row])) : String(row[c as keyof typeof row] ?? '-')}</td>)}</tr>)}</tbody>
        </table>
      </div>

      <div className="flex items-center justify-between">
        <span className="text-sm text-gray-500">Page {page + 1} of {totalPages}</span>
        <div className="flex gap-2">
          <button disabled={page === 0} onClick={() => setPage(page - 1)} className="px-3 py-1 text-sm border rounded disabled:opacity-50">Prev</button>
          <button disabled={page >= totalPages - 1} onClick={() => setPage(page + 1)} className="px-3 py-1 text-sm border rounded disabled:opacity-50">Next</button>
        </div>
      </div>
    </div>
  );
}
