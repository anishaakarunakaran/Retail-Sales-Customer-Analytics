'use client';
import { useData } from '@/lib/context';
import { exportTransactionsCSV, exportExcel } from '@/lib/exports';

export default function SettingsPage() {
  const { rawData, datasetName, loadDataset, uploadDataset } = useData();

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) await uploadDataset(file);
  };

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-gray-900">Settings</h2>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-4">
          <h3 className="text-lg font-semibold text-gray-800">Dataset Management</h3>
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <button onClick={() => loadDataset('Retail Sales Demo')} className="px-4 py-2 text-sm bg-blue-600 text-white rounded-md">Load Demo Dataset</button>
              <span className="text-sm text-gray-500">32,000 records</span>
            </div>
            <div>
              <label className="block text-sm text-gray-600 mb-1">Upload Custom Dataset</label>
              <input type="file" accept=".csv,.xlsx" onChange={handleUpload} className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:bg-gray-600 file:text-white" />
            </div>
            <div className="p-3 bg-gray-50 rounded text-sm">
              <div>Current: <strong>{datasetName || 'None'}</strong></div>
              <div>Rows: <strong>{rawData.length.toLocaleString()}</strong></div>
            </div>
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-4">
          <h3 className="text-lg font-semibold text-gray-800">Export Data</h3>
          <div className="space-y-2">
            <button onClick={() => exportTransactionsCSV(rawData, `${datasetName.replace(/\s+/g, '_')}.csv`)} className="block w-full px-4 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-md text-left">Export as CSV</button>
            <button onClick={() => exportExcel(rawData as unknown as Record<string, unknown>[], `${datasetName.replace(/\s+/g, '_')}.xlsx`)} className="block w-full px-4 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-md text-left">Export as Excel</button>
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-4">
          <h3 className="text-lg font-semibold text-gray-800">About RetailIQ</h3>
          <div className="text-sm text-gray-600 space-y-2">
            <p>Retail Sales & Customer Analytics Platform. Built with Next.js, TypeScript, Tailwind CSS, Recharts, and SQL.js.</p>
            <p>All analytics are computed from the loaded dataset. No fake data, no hardcoded metrics.</p>
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-4">
          <h3 className="text-lg font-semibold text-gray-800">Data Dictionary</h3>
          <div className="text-sm text-gray-600 space-y-1 max-h-60 overflow-y-auto">
            {rawData.length > 0 && Object.keys(rawData[0]).map((k) => (
              <div key={k} className="flex justify-between border-b pb-1"><span className="font-medium">{k}</span><span className="text-gray-400">{typeof rawData[0][k as keyof typeof rawData[0]]}</span></div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
