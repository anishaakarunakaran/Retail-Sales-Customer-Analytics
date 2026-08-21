import type { Metadata } from 'next';
import './globals.css';
import AppLayout from '@/components/AppLayout';

export const metadata: Metadata = {
  title: 'RetailIQ - Retail Sales & Customer Analytics Platform',
  description: 'Turn retail data into actionable business insights.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="antialiased bg-gray-50">
        <AppLayout>{children}</AppLayout>
      </body>
    </html>
  );
}
