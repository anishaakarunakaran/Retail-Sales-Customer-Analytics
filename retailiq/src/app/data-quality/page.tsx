'use client';
import { useData } from '@/lib/context';
import { detectDataQuality, cleanData } from '@/lib/validation';
import { useState } from 'react';

export default function DataQualityPage() {
  const { rawData, filteredData, uploadDataset } = useData();
  const [testData, setTestData] = useState<Record<string, unknown>[] | null>(null);
  const [qualityReport, setQualityReport] = useState<ReturnType<typeof detectDataQuality> | null>(null);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      await uploadDataset(file);
      setQualityReport(null);
      setTestData(null);
    }
  };

  const runQualityCheck = () => {
    const report = detectDataQuality(rawData.length > 0 ? rawData : filteredData);
    setQualityReport(report);
  };

  const runClean = () => {
    const cleaned = cleanData(rawData.length > 0 ? rawData : filteredData);
    setTestData(cleaned as unknown as Record<string, unknown>[]);
  };

  const data = rawData.length > 0 ? rawData : filteredData;

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-gray-900">Data Quality</h2>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">Upload Dataset</h3>
          <input type="file" accept=".csv,.xlsx" onChange={handleUpload} className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:bg-blue-600 file:text-white" />
          <p className="text-xs text-gray-400 mt-2">Supports CSV and XLSX files</p>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">Dataset Info</h3>
          <div className="space-y-1 text-sm">
            <div>Rows: <strong>{data.length.toLocaleString()}</strong></div>
            <div>Columns: <strong>{data.length > 0 ? Object.keys(data[0]).length : 0}</strong></div>
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">Actions</h3>
          <div className="flex gap-2">
            <button onClick={runQualityCheck} className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded-md">Run Quality Check</button>
            <button onClick={runClean} className="px-3 py-1.5 text-sm bg-emerald-600 text-white rounded-md">Clean Data</button>
          </div>
        </div>
      </div>

      {qualityReport && (
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">Data Quality Report</h3>
          <div className="grid grid-cols-3 gap-4 mb-4">
            <div className="text-center"><div className="text-2xl font-bold text-gray-900">{qualityReport.totalRows.toLocaleString()}</div><div className="text-xs text-gray-500">Total Rows</div></div>
            <div className="text-center"><div className="text-2xl font-bold text-emerald-600">{qualityReport.validRows.toLocaleString()}</div><div className="text-xs text-gray-500">Valid Rows</div></div>
            <div className="text-center"><div className="text-2xl font-bold text-red-600">{qualityReport.totalRows - qualityReport.validRows}</div><div className="text-xs text-gray-500">Issues Found</div></div>
          </div>
          <table className="w-full text-sm">
            <thead><tr className="border-b text-left text-gray-500"><th className="py-2">Issue Type</th><th className="py-2 text-right">Count</th><th className="py-2">Severity</th><th className="py-2">Description</th></tr></thead>
            <tbody>{qualityReport.issues.map((issue, i) => <tr key={i} className="border-b"><td className="py-2 font-medium">{issue.type}</td><td className="py-2 text-right">{issue.count}</td><td className="py-2"><span className={`text-xs px-2 py-0.5 rounded-full ${issue.severity === 'high' ? 'bg-red-100 text-red-700' : issue.severity === 'medium' ? 'bg-amber-100 text-amber-700' : 'bg-gray-100 text-gray-600'}`}>{issue.severity}</span></td><td className="py-2 text-gray-600">{issue.description}</td></tr>)}</tbody>
          </table>
        </div>
      )}

      {testData && (
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">Cleaned Data Preview ({testData.length} rows)</h3>
          <p className="text-xs text-gray-500">Cleaned from {data.length} to {testData.length} rows ({data.length - testData.length} removed)</p>
        </div>
      )}
    </div>
  );
}
