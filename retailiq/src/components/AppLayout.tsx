'use client';
import { DataProvider, useData } from '@/lib/context';
import { Sidebar } from '@/components/Sidebar';
import { FilterPanel } from '@/components/FilterPanel';

function LoadingOverlay() {
  const { loading } = useData();
  if (!loading) return null;
  return (
    <div className="fixed inset-0 bg-white/80 z-50 flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-3" />
        <p className="text-sm text-gray-600">Loading dataset...</p>
      </div>
    </div>
  );
}

function AppContent({ children }: { children: React.ReactNode }) {
  const { datasetName } = useData();
  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between">
          <h1 className="text-lg font-semibold text-gray-900">RetailIQ</h1>
          <div className="flex items-center gap-3 text-sm text-gray-500">
            <span>Dataset: <strong className="text-gray-700">{datasetName || 'None loaded'}</strong></span>
          </div>
        </header>
        <main className="flex-1 overflow-y-auto p-6">
          <FilterPanel />
          {children}
        </main>
      </div>
      <LoadingOverlay />
    </div>
  );
}

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <DataProvider>
      <AppContent>{children}</AppContent>
    </DataProvider>
  );
}
