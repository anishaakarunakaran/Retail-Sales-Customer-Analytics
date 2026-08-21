'use client';
import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from 'react';
import type { Transaction, FilterState } from '@/lib/types';
import { DEFAULT_FILTERS } from '@/lib/types';
import { loadDemoData, processRawData, applyFilters, getUniqueValues } from '@/lib/data';

interface DataContextType {
  rawData: Transaction[];
  filteredData: Transaction[];
  filters: FilterState;
  setFilters: (f: FilterState) => void;
  loading: boolean;
  datasetName: string;
  loadDataset: (name: string) => Promise<void>;
  uploadDataset: (file: File) => Promise<void>;
  filterOptions: Record<string, string[]>;
}

const DataContext = createContext<DataContextType | null>(null);

export function DataProvider({ children }: { children: ReactNode }) {
  const [rawData, setRawData] = useState<Transaction[]>([]);
  const [filters, setFilters] = useState<FilterState>(DEFAULT_FILTERS);
  const [loading, setLoading] = useState(false);
  const [datasetName, setDatasetName] = useState('');

  const filteredData = applyFilters(rawData, filters);

  const filterOptions = {
    regions: getUniqueValues(rawData, 'region'),
    states: getUniqueValues(rawData, 'customer_state'),
    cities: getUniqueValues(rawData, 'customer_city'),
    categories: getUniqueValues(rawData, 'category'),
    subcategories: getUniqueValues(rawData, 'subcategory'),
    brands: getUniqueValues(rawData, 'brand'),
    customerSegments: getUniqueValues(rawData, 'customer_segment'),
    genders: getUniqueValues(rawData, 'customer_gender'),
    ageGroups: getUniqueValues(rawData, 'age_group'),
    paymentMethods: getUniqueValues(rawData, 'payment_method'),
    salesChannels: getUniqueValues(rawData, 'sales_channel'),
    storeTypes: getUniqueValues(rawData, 'store_type'),
  };

  const loadDataset = useCallback(async (name: string) => {
    setLoading(true);
    try {
      const data = await loadDemoData();
      setRawData(data);
      setDatasetName(name);
    } catch (e) { console.error('Failed to load dataset:', e); }
    setLoading(false);
  }, []);

  const uploadDataset = useCallback(async (file: File) => {
    setLoading(true);
    try {
      const text = await file.text();
      const Papa = (await import('papaparse')).default;
      const result = Papa.parse(text, { header: true, skipEmptyLines: true, dynamicTyping: true });
      const data = processRawData(result.data as Transaction[]);
      setRawData(data);
      setDatasetName(file.name);
    } catch (e) { console.error('Failed to parse upload:', e); }
    setLoading(false);
  }, []);

  useEffect(() => {
    loadDataset('Retail Sales Demo');
  }, [loadDataset]);

  return (
    <DataContext.Provider value={{ rawData, filteredData, filters, setFilters, loading, datasetName, loadDataset, uploadDataset, filterOptions }}>
      {children}
    </DataContext.Provider>
  );
}

export function useData() {
  const ctx = useContext(DataContext);
  if (!ctx) throw new Error('useData must be used within DataProvider');
  return ctx;
}
