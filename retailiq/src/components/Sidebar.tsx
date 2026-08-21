'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { classNames } from '@/lib/utils';
import { useState } from 'react';

const NAV = [
  { href: '/', label: 'Overview' },
  { href: '/sales', label: 'Sales Analytics' },
  { href: '/products', label: 'Product Analytics' },
  { href: '/customers', label: 'Customer Analytics' },
  { href: '/rfm', label: 'RFM Segmentation' },
  { href: '/statistics', label: 'Statistics' },
  { href: '/insights', label: 'Business Insights' },
  { href: '/explorer', label: 'Data Explorer' },
  { href: '/playground', label: 'Data Playground' },
  { href: '/data-quality', label: 'Data Quality' },
  { href: '/sql', label: 'SQL Analytics' },
  { href: '/reports', label: 'Reports' },
  { href: '/settings', label: 'Settings' },
];

export function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside className={classNames(
      'flex flex-col bg-gray-900 text-white transition-all duration-200 border-r border-gray-800',
      collapsed ? 'w-16' : 'w-56'
    )}>
      <div className="flex items-center justify-between px-4 py-4 border-b border-gray-800">
        {!collapsed && <span className="font-bold text-lg tracking-tight">RetailIQ</span>}
        <button onClick={() => setCollapsed(!collapsed)} className="text-gray-400 hover:text-white text-sm p-1">
          {collapsed ? '\u2192' : '\u2190'}
        </button>
      </div>
      <nav className="flex-1 overflow-y-auto py-2">
        {NAV.map((item) => (
          <Link key={item.href} href={item.href} className={classNames(
            'flex items-center gap-2 px-3 py-2 mx-1 rounded text-sm transition-colors',
            pathname === item.href ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white hover:bg-gray-800'
          )}>
            {!collapsed && <span>{item.label}</span>}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
