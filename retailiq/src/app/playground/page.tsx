'use client';
import { useData } from '@/lib/context';
import { useState, useMemo } from 'react';

export default function PlaygroundPage() {
  const { rawData } = useData();
  const [columns, setColumns] = useState<string[]>([]);
  const [sortField, setSortField] = useState('');
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('asc');
  const [groupField, setGroupField] = useState('');
  const [aggField, setAggField] = useState('sales_amount');
  const [aggFn, setAggFn] = useState<'sum' | 'avg' | 'count' | 'min' | 'max'>('sum');
  const [filterText, setFilterText] = useState('');
  const [view, setView] = useState<'table' | 'aggregate'>('table');

  const allCols = rawData.length > 0 ? Object.keys(rawData[0]) : [];
  const numericCols = allCols.filter((c) => typeof rawData[0]?.[c as keyof typeof rawData[0]] === 'number');

  const processed = useMemo(() => {
    let data = [...rawData];
    if (filterText) {
      const q = filterText.toLowerCase();
      data = data.filter((r) => Object.values(r).some((v) => String(v).toLowerCase().includes(q)));
    }
    if (columns.length > 0) {
      data = data.map((r) => Object.fromEntries(columns.map((c) => [c, r[c as keyof typeof r]]))) as unknown as typeof data;
    }
    if (sortField) {
      data.sort((a, b) => {
        const av = Number(a[sortField as keyof typeof a]) || 0;
        const bv = Number(b[sortField as keyof typeof b]) || 0;
        return sortDir === 'asc' ? av - bv : bv - av;
      });
    }
    return data;
  }, [rawData, columns, sortField, sortDir, filterText]);

  const aggregated = useMemo(() => {
    if (!groupField) return [];
    const map = new Map<string, number[]>();
    rawData.forEach((r) => {
      const key = String(r[groupField as keyof typeof r]);
      if (!map.has(key)) map.set(key, []);
      map.get(key)!.push(Number(r[aggField as keyof typeof r]) || 0);
    });
    return Array.from(map.entries()).map(([key, vals]) => {
      let val = 0;
      if (aggFn === 'sum') val = vals.reduce((a, b) => a + b, 0);
      else if (aggFn === 'avg') val = vals.reduce((a, b) => a + b, 0) / vals.length;
      else if (aggFn === 'count') val = vals.length;
      else if (aggFn === 'min') val = Math.min(...vals);
      else if (aggFn === 'max') val = Math.max(...vals);
      return { [groupField]: key, [`${aggFn}(${aggField})`]: val, count: vals.length };
    }).sort((a, b) => {
      const key = `${aggFn}(${aggField})`;
      return (Number(b[key]) || 0) - (Number(a[key]) || 0);
    });
  }, [rawData, groupField, aggField, aggFn]);

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold text-gray-900">Data Playground</h2>
      <p className="text-sm text-gray-500">Manipulate data without changing the original. {rawData.length} rows loaded.</p>

      <div className="flex gap-2 mb-4">
        <button onClick={() => setView('table')} className={`px-3 py-1.5 text-sm rounded-md border ${view === 'table' ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-gray-600 border-gray-300'}`}>Table View</button>
        <button onClick={() => setView('aggregate')} className={`px-3 py-1.5 text-sm rounded-md border ${view === 'aggregate' ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-gray-600 border-gray-300'}`}>Aggregate</button>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-4 space-y-3">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div>
            <label className="block text-xs text-gray-500 mb-1">Filter</label>
            <input type="text" value={filterText} onChange={(e) => setFilterText(e.target.value)} placeholder="Search all columns..." className="w-full px-2 py-1.5 text-sm border rounded" />
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">Sort By</label>
            <select value={sortField} onChange={(e) => setSortField(e.target.value)} className="w-full px-2 py-1.5 text-sm border rounded">
              <option value="">None</option>{numericCols.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">Direction</label>
            <select value={sortDir} onChange={(e) => setSortDir(e.target.value as 'asc' | 'desc')} className="w-full px-2 py-1.5 text-sm border rounded">
              <option value="asc">Ascending</option><option value="desc">Descending</option>
            </select>
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">Columns</label>
            <select multiple value={columns} onChange={(e) => setColumns(Array.from(e.target.selectedOptions, (o) => o.value))} className="w-full px-2 py-1.5 text-sm border rounded h-20">
              {allCols.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
        </div>

        {view === 'aggregate' && (
          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block text-xs text-gray-500 mb-1">Group By</label>
              <select value={groupField} onChange={(e) => setGroupField(e.target.value)} className="w-full px-2 py-1.5 text-sm border rounded">
                <option value="">Select...</option>{allCols.map((c) => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">Aggregate Field</label>
              <select value={aggField} onChange={(e) => setAggField(e.target.value)} className="w-full px-2 py-1.5 text-sm border rounded">
                {numericCols.map((c) => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">Function</label>
              <select value={aggFn} onChange={(e) => setAggFn(e.target.value as typeof aggFn)} className="w-full px-2 py-1.5 text-sm border rounded">
                {['sum', 'avg', 'count', 'min', 'max'].map((f) => <option key={f} value={f}>{f.toUpperCase()}</option>)}
              </select>
            </div>
          </div>
        )}
      </div>

      <div className="bg-white border border-gray-200 rounded-lg overflow-x-auto">
        {view === 'table' ? (
          <table className="w-full text-sm">
            <thead><tr className="border-b bg-gray-50">{(columns.length > 0 ? columns : allCols).slice(0, 12).map((c) => <th key={c} className="py-2 px-2 text-left text-gray-600">{c}</th>)}</tr></thead>
            <tbody>{processed.slice(0, 50).map((r, i) => <tr key={i} className="border-b hover:bg-gray-50">{(columns.length > 0 ? columns : allCols).slice(0, 12).map((c) => <td key={c} className="py-1.5 px-2 truncate max-w-[150px]">{String(r[c as keyof typeof r] ?? '-')}</td>)}</tr>)}</tbody>
          </table>
        ) : (
          <table className="w-full text-sm">
            <thead><tr className="border-b bg-gray-50">{aggregated.length > 0 && Object.keys(aggregated[0]).map((c) => <th key={c} className="py-2 px-2 text-left text-gray-600">{c}</th>)}</tr></thead>
            <tbody>{aggregated.map((r, i) => <tr key={i} className="border-b">{Object.values(r).map((v, j) => <td key={j} className="py-1.5 px-2">{typeof v === 'number' ? v.toLocaleString(undefined, { maximumFractionDigits: 2 }) : String(v)}</td>)}</tr>)}</tbody>
          </table>
        )}
      </div>
      <div className="text-xs text-gray-400">Showing {view === 'table' ? Math.min(50, processed.length) : aggregated.length} rows</div>
    </div>
  );
}
