'use client';
import { useState, useEffect } from 'react';
import { initDB, loadTransactionsToDB, runQuery, PRESET_QUERIES } from '@/lib/sql';
import { useData } from '@/lib/context';

export default function SQLPage() {
  const { rawData } = useData();
  const [sql, setSql] = useState(PRESET_QUERIES[0].sql);
  const [result, setResult] = useState<{ columns: string[]; rows: (string | number | null)[][] } | null>(null);
  const [dbReady, setDbReady] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    (async () => {
      await initDB();
      if (rawData.length > 0) {
        loadTransactionsToDB(rawData);
        setDbReady(true);
      }
    })();
  }, [rawData]);

  const executeQuery = () => {
    if (!dbReady) return;
    setLoading(true);
    try {
      const res = runQuery(sql);
      setResult(res);
    } catch (e) { setResult({ columns: ['Error'], rows: [[String(e)]] }); }
    setLoading(false);
  };

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold text-gray-900">SQL Analytics</h2>
      <p className="text-sm text-gray-500">Run SQL queries against the loaded dataset using in-browser SQLite (SQL.js).</p>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        <div className="bg-white border border-gray-200 rounded-lg p-3">
          <h3 className="text-xs font-semibold text-gray-500 uppercase mb-2">Preset Queries</h3>
          <div className="space-y-1 max-h-96 overflow-y-auto">
            {PRESET_QUERIES.map((q, i) => (
              <button key={i} onClick={() => setSql(q.sql)} className="w-full text-left text-sm px-2 py-1.5 rounded hover:bg-gray-100 text-gray-700">{q.name}</button>
            ))}
          </div>
        </div>

        <div className="lg:col-span-3 space-y-4">
          <div>
            <textarea value={sql} onChange={(e) => setSql(e.target.value)} rows={6} className="w-full p-3 text-sm font-mono border border-gray-300 rounded-lg bg-gray-50" placeholder="SELECT * FROM transactions LIMIT 10" />
            <div className="flex items-center gap-3 mt-2">
              <button onClick={executeQuery} disabled={!dbReady || loading} className="px-4 py-2 text-sm bg-blue-600 text-white rounded-md disabled:opacity-50">
                {loading ? 'Running...' : 'Execute Query'}
              </button>
              <span className="text-xs text-gray-400">{dbReady ? `Table loaded: ${rawData.length} rows` : 'Loading database...'}</span>
            </div>
          </div>

          {result && (
            <div className="bg-white border border-gray-200 rounded-lg overflow-x-auto">
              <div className="px-4 py-2 border-b text-xs text-gray-500">{result.rows.length} rows returned</div>
              <table className="w-full text-sm">
                <thead><tr className="border-b bg-gray-50">{result.columns.map((c) => <th key={c} className="py-2 px-3 text-left text-gray-600">{c}</th>)}</tr></thead>
                <tbody>{result.rows.slice(0, 100).map((row, i) => <tr key={i} className="border-b hover:bg-gray-50">{row.map((cell, j) => <td key={j} className="py-1.5 px-3">{typeof cell === 'number' ? cell.toLocaleString(undefined, { maximumFractionDigits: 2 }) : String(cell ?? '-')}</td>)}</tr>)}</tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
