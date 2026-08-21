'use client';
import { useData } from '@/lib/context';
import { useState } from 'react';

export function FilterPanel() {
  const { filters, setFilters, filterOptions } = useData();
  const [expanded, setExpanded] = useState(false);

  const toggle = (field: keyof typeof filters, value: string) => {
    const current = filters[field] as string[];
    const next = current.includes(value) ? current.filter((v) => v !== value) : [...current, value];
    setFilters({ ...filters, [field]: next });
  };

  const reset = () => setFilters({
    dateRange: null, regions: [], states: [], cities: [], categories: [], subcategories: [],
    brands: [], customerSegments: [], genders: [], ageGroups: [], paymentMethods: [], salesChannels: [], storeTypes: [],
  });

  const activeCount = Object.values(filters).reduce((acc, v) => {
    if (Array.isArray(v)) return acc + v.length;
    if (v && Array.isArray(v)) return acc + 1;
    return acc;
  }, 0);

  const filterGroups = [
    { key: 'regions' as const, label: 'Region', options: filterOptions.regions },
    { key: 'categories' as const, label: 'Category', options: filterOptions.categories },
    { key: 'customerSegments' as const, label: 'Segment', options: filterOptions.customerSegments },
    { key: 'salesChannels' as const, label: 'Channel', options: filterOptions.salesChannels },
    { key: 'paymentMethods' as const, label: 'Payment', options: filterOptions.paymentMethods },
    { key: 'storeTypes' as const, label: 'Store Type', options: filterOptions.storeTypes },
    { key: 'genders' as const, label: 'Gender', options: filterOptions.genders },
    { key: 'ageGroups' as const, label: 'Age Group', options: filterOptions.ageGroups },
  ];

  return (
    <div className="bg-white border border-gray-200 rounded-lg mb-4">
      <div className="flex items-center justify-between px-4 py-2 cursor-pointer" onClick={() => setExpanded(!expanded)}>
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-gray-700">Filters</span>
          {activeCount > 0 && (
            <span className="bg-blue-100 text-blue-700 text-xs font-medium px-2 py-0.5 rounded-full">
              {activeCount} active
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {activeCount > 0 && (
            <button onClick={(e) => { e.stopPropagation(); reset(); }} className="text-xs text-red-600 hover:text-red-800">
              Reset All
            </button>
          )}
          <span className="text-gray-400 text-sm">{expanded ? '\u25B2' : '\u25BC'}</span>
        </div>
      </div>

      {expanded && (
        <div className="px-4 pb-4 grid grid-cols-2 md:grid-cols-4 gap-3">
          {filterGroups.map((group) => (
            <div key={group.key}>
              <label className="block text-xs font-medium text-gray-500 mb-1">{group.label}</label>
              <div className="max-h-32 overflow-y-auto space-y-0.5">
                {group.options.map((opt) => (
                  <label key={opt} className="flex items-center gap-1.5 text-sm text-gray-700 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={(filters[group.key] as string[]).includes(opt)}
                      onChange={() => toggle(group.key, opt)}
                      className="rounded border-gray-300"
                    />
                    <span className="truncate">{opt}</span>
                  </label>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
